import re
import pprint
import json
from collections import defaultdict
# For the scraping and User Agent generation
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
# data to sql
import mysql.connector
from datetime import datetime
#threading
import threading
import time

start_time = time.time()

# Get the current date
current_date = datetime.now()

# Lock initialization
lock = threading.Lock()

# Format the date as DD_MM_YYYY
formatted_date = current_date.strftime("_%d_%m_%Y")

# A list of all the Button Names
# all_actions = ["Buy", "Rent"]
all_actions = ["Rent"] #!!!

# We need a List of All City Names
#Kefallinia
#Lefkada
#Zakynthos
#Kerkyra

#Kyklades
#Mytilini
#Rodos
#Samos
#Chios
#Chalkida
all_cities = [
        #Land
            "AgiosNikolaos", "Amfissa", "Arta", "Athens", "Alexandroupoli",
            "Veroia", "Volos",
            "Grevena",
            "Drama",
            "Edessa", "Elefsina", 
            "Igoumenitsa", "Irakleio",
            "Thessaloniki",
            "Ioannina",
            "Kavala", "Kalamata", "Karditsa", "Karpenisi", "Kastoria", "Katerini", "Kilkis", "Kozani", "Komotini", "Korinthos", 
            "Larisa", "Lamia", "Livadia",
            "Mesologgi",
            "Nafplio",
            "Xanthi",
            "Patra", "Preveza", "Pyrgos",
            "Rethymno",
            "Serres", "Sparti",
            "Trikala", "Tripoli",
            "Florina",
            "Chalkidiki",
            "Chania"
            ]

# A dictionary where key:City and values are all provinces of that particular city
dict_cities_provinces = {
                        "Athens": ["AthensCentre", "AthensEast", "AthensNorth", "AthensWest", "AthensSouth", "Peiraias", "PeiraiasSuburbs", "AtticaRest", "ArgosaronikosIslands", "AgiaVarvara", "AgiaParaskevi", "AgioiAnargiroi", "AgiosDimitrios", "AgiosEleftherios", "AgiosIoannisRentis"],
                        "Thessaloniki": ["Municipality", "RegionalMunicipality", "DistrictRest", "40Ekklisies", "AgiaSofia", "AgiosGeorgios", "AgiosPavlos", "Ampelokipoi", "Analipsi", "Antigonidon", "AnoPoli"]
                        }

all_table_names = []
for action in all_actions:
    for city in all_cities:
        provinces = dict_cities_provinces.get(city)
        if provinces:
            all_table_names.extend([f"{action}_{city}_{province}" for province in provinces])
        else:
            all_table_names.append(f"{action}_{city}")

pprint.pprint(all_table_names)
print(len(all_table_names), "tables.")

# A dictionary of tables and their corresponding url so it is easily updatale MANUALLY
dict_table_url = {
                'example_table_name1': 'example.url1',
                'example_table_name2': 'example.url2',
                'example_table_name3': 'example.url3',
                }

# Proxy Setup
HOSTNAME = 'gr.smartproxy.com'
PORT = '30000'
proxy= '{hostname}:{port}'.format(hostname=HOSTNAME, port=PORT)

def Scraper(table_name):

    time.sleep(random.uniform(1, 6)) # Wait from 1 to 6 seconds randomly

    sqmeters = []
    price = []

    conn = None
    cursor = None

    try:
        # Connect to the database
        conn = mysql.connector.connect(
            host="localhost",
            user="panagos",
            password="password",
            database="mydatabase"
        )
        cursor = conn.cursor()

        with lock:

            # Check if the table exists
            cursor.execute(f"SHOW TABLES LIKE '{table_name+formatted_date}';")
            result = cursor.fetchone()
            if result:
                print(f"\nTable {table_name+formatted_date} already exists, Marking as successful without scraping.")
                return True  # Return True to indicate skipping
            cursor.close()
            conn.close()
            # If table does not exist, continue with scraping
            print(f"\nTable {table_name+formatted_date} does not exist, proceeding with scraping...")

    except mysql.connector.Error as error:
        print(f"\nDatabase error: {error}\n")
        return False
    
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

    try:

        action = 'No Action'
        url = 'No Url'

        # From the table name get  the corresponding link
        for table in dict_table_url.keys():
            if table == table_name:
                url = dict_table_url[table_name]
    
        # From table name get Rent or Buy
        if table_name.startswith('Rent'):
            action = 'Rent'
        if table_name.startswith("Buy"):
            action = 'Buy'

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')

        # Disable images (does not reduce proxy data usage)
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        
        options.add_argument('--proxy-server={}'.format(proxy))

        # Mimicking a regular user's browser to avoid detection.
        def generate_dynamic_chrome_user_agent():
            # Simplified base string with essential components
            base_string = "Mozilla/5.0 ({os}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36"

            os_to_chrome_versions = {
                "Windows NT 10.0; Win64; x64": ["121.0.6167.140", "121.0.6167.139", "121.0.6167.85", "121.0.6167.86", "120.0.6099.268", "120.0.6099.276", "121.0.6167.85"],
                "Macintosh; Intel Mac OS X 10_15_7": ["121.0.6167.139", "121.0.6167.85", "120.0.6099.268", "120.0.6099.276", "121.0.6167.85"],
                "Macintosh; Intel Mac OS X 11_7_10": ["121.0.6167.139", "121.0.6167.85", "120.0.6099.268", "120.0.6099.276", "121.0.6167.85"],
                "X11; Linux x86_64": ["121.0.6167.139", "121.0.6167.85"]
            }

            os_keys = list(os_to_chrome_versions.keys())
            random.shuffle(os_keys)

            # Choose a random operating system
            os = random.choice(os_keys)

            # Shuffle the list of Chrome versions for the chosen OS
            chrome_versions = os_to_chrome_versions[os]
            random.shuffle(chrome_versions)

            # Choose a random Chrome version
            version = random.choice(chrome_versions)
            
            # Format and add the user agent to the list
            user_agent = base_string.format(os=os, chrome_version=version)

            return user_agent

        user_agent = generate_dynamic_chrome_user_agent()
        print("Agent:", user_agent)

        options.add_argument(f'user-agent={user_agent}')  # Set a user agent

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        driver.get(url)

        driver.implicitly_wait(10)

        # CAPTCHA checks
        captcha_indicators = ["I am not a robot", "CAPTCHA", "captcha"]
        captcha_found = False
        for indicator in captcha_indicators:
            if driver.find_elements(By.XPATH, f"//*[contains(text(), '{indicator}')]"):
                captcha_found = True
                break

        # Check for reCAPTCHA iframe using its class
        if not captcha_found and driver.find_elements(By.CSS_SELECTOR, "iframe[src*='recaptcha']"):
            captcha_found = True

        # CAPTCHA is detected
        if captcha_found:
            print(f"\nCAPTCHA detected on {url}. Consider manual intervention or a different scraping strategy.////////////////////////////////////\n")

        print(driver.title)

        # Extract all text from the webpage
        text = driver.find_element(By.TAG_NAME, 'body').text
        # print(text)
        driver.close()

        def remove_lines_by_length(text):
            # Split the text into individual lines
            lines = text.split('\n')
            
            # Filter out lines that are shorter than 4 characters or longer than 30 characters
            filtered_lines = [line for line in lines if 4 <= len(line) <= 30]
            
            # Reassemble text 
            modified_text = '\n'.join(filtered_lines)
            
            return modified_text

        text = remove_lines_by_length(text)
        # print(text)
        # print("///////////////////////////////////////////////////")

        def delete_lines_after_pattern_until_euro(text, pattern):
            lines = text.splitlines()
            new_lines = []
            # Indicates if we are currently skipping lines
            skip_lines = False  

            for line in lines:
                # If we're not skipping, look for a pattern match
                if not skip_lines and re.search(pattern, line):
                    new_lines.append(line)  # Add the matching line
                    skip_lines = True  # Start skipping lines
                # If we are skipping and find a line starting with '€'
                elif skip_lines and line.startswith('€'):
                    new_lines.append(line)  # Add this line
                    skip_lines = False  # Stop skipping

            return "\n".join(new_lines)

        text = delete_lines_after_pattern_until_euro(text,r'τ\.μ\.$|m²$')
        # print(text)

        if action=='Buy':
            def delete_second_euro_line(input_text):
                lines = input_text.split('\n')
                processed_lines = []
                prev_line_starts_with_euro = False
                for line in lines:
                    current_line_starts_with_euro = line.startswith('€')
                    if not (current_line_starts_with_euro and prev_line_starts_with_euro):
                        processed_lines.append(line)
                    prev_line_starts_with_euro = current_line_starts_with_euro
                return '\n'.join(processed_lines)
            text = delete_second_euro_line(text)
            # print(text)

        #Sq Meters
        sqmeters = re.findall(r',.*(?=τ\.μ\.)|,.*(?=m²)', text)
        #Price
        if action=='Buy':
            price = re.findall(r'€(.*)', text)
        if action=='Rent':
            price = re.findall(r'€(.*)/', text) 

        # Numbers cleanup
        def ExtractNumbers(my_list):
            processed_list = []
            for s in my_list:
                # Replace non digit characters with an empty string
                numbers_only = re.sub(r'\D', '', s)
                processed_list.append(numbers_only)
            return processed_list
        
        print('\n')
        print('///////////////////////////////////////////////////////////////////////////////////')
        sqmeters = ExtractNumbers(sqmeters)
        print(f'{table_name} Sq.Meters:', sqmeters, 'size:', len(sqmeters)) 
        price = ExtractNumbers(price)
        print(f'{table_name} Price:', price, 'size:', (len(price)))
        print('\n')

        if len(sqmeters) > 0 and len(price) > 0:
            if len(sqmeters) == len(price):
                sqmeters_price_dict = defaultdict(list)
                for sqm, p in zip(sqmeters, price):
                    sqmeters_price_dict[int(sqm)].append(int(p))
                sqmeters_price_dict = dict(sqmeters_price_dict)
                pprint.pprint(sqmeters_price_dict)
            else:
                print(f'\n!ERROR: NOT EQUAL LIST LENGTHS! for {table_name}.\n')
        else:
            if len(sqmeters) == 0 or len(price) == 0:
                print(f'\n!ERROR: sqmeters AND price list are EMPTY! for {table_name}.\n')

        # Average price per home size Dictionary
        def GetDictAverage(dictionary):
            average = []
            dict_values = list(dictionary.values()) 
            for i in range(len(dict_values)):
                average.append(int(sum(dict_values[i])/len(dict_values[i])))
            average_dictionary = {key: value for key, value in zip(dictionary.keys(), average)}  
            return(average_dictionary)

        average_sqmeters_price_dict = GetDictAverage(sqmeters_price_dict)
        # print("\nAverage price per home size:\n")
        # pprint.pprint(average_sqmeters_price_dict)

        # Overall average suare meter price
        def SquareMeterPrice(dictionary):
            meters = sum(dictionary.keys())
            prices = sum(dictionary.values())
            meter_price = round(prices / meters, 2)
            return(meter_price)

        price_per_sqmeter = SquareMeterPrice(average_sqmeters_price_dict)
        print(f"\nAVERAGE PRICE PER SQUARE METER for {table_name}:",price_per_sqmeter,"€.")
        print(f"Scraping for {table_name} was successful.\n")


        # Data to SQL
        with lock:
            
            conn = mysql.connector.connect(
                host="localhost",
                user="panagos",
                password="password",
                database="mydatabase"
            )
            cursor = conn.cursor()

            # Create the table name with the current date
            table_name_with_date = f"{table_name}{formatted_date}"

            sql_command = f"""CREATE TABLE IF NOT EXISTS {table_name_with_date} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                date DATE,
                size VARCHAR(255),
                price VARCHAR(255),
                ppm FLOAT  
            );"""

            cursor.execute(sql_command)

            # Data to be inserted
            data = [
                {
                    "date": datetime.now().date(),  # Current date
                    "sizes_prices": average_sqmeters_price_dict,
                    "ppm": price_per_sqmeter
                }
            ]

            # Insert data
            for entry in data:
                current_date = entry["date"]
                sizes_prices = entry["sizes_prices"]
                ppm = entry["ppm"]
                for size, price in sizes_prices.items():
                    sql = f"INSERT INTO {table_name_with_date} (date, size, price, ppm) VALUES (%s, %s, %s, %s)"
                    val = (current_date, str(size), str(price), ppm)
                    cursor.execute(sql, val)

            conn.commit()
            # Close connection
            cursor.close()
            conn.close()

        print("\nAction:",action)
        print("\nUrl:",url)
        print("\n")
        return True

    except Exception as e:
        print(f"Scraping failed for {table_name}. Error: {str(e)}\n")
        return False

# Threading
def scraping_task(table_names_subset, proxy):
    successful_scrapes = 0  # Counter for successful scrapes
    total_scrapes = len(table_names_subset)
    
    for table_name in table_names_subset:
        scraping_successful = False

        while not scraping_successful:
            
            if not proxy:
                print("Failed to fetch proxy. Retrying...")
                time.sleep(10)  # Wait for 10 seconds before retrying to fetch new proxies
                continue  # Skip the rest of the loop and try fetching proxies again
            
            print("Proxy fetched.")

            scraping_successful = Scraper(table_name)

            if not scraping_successful:
                print(f"Scraping for {table_name} failed with proxy {proxy}. Trying again...")
                time.sleep(random.uniform(5, 10))

            print(f"Current success rate: {successful_scrapes}/{total_scrapes} ({successful_scrapes/total_scrapes*100:.2f}%)")

        print(f"Scraping successful for {table_name}.")
        successful_scrapes+=1
        
    print(f"Final success rate: {successful_scrapes}/{total_scrapes} ({successful_scrapes/total_scrapes*100:.2f}%)")
    print("Scraping task completed.")

total_tables = len(all_table_names)
quarter_length = total_tables // 4

# Splitting the list of table names into four parts
first_quarter = all_table_names[:quarter_length]
second_quarter = all_table_names[quarter_length:2 * quarter_length]
third_quarter = all_table_names[2 * quarter_length:3 * quarter_length]
fourth_quarter = all_table_names[3 * quarter_length:]

# Creating threads
# thread1 = threading.Thread(target=scraping_task, args=(['Buy_Thessaloniki_Ampelokipoi'], proxies))
thread1 = threading.Thread(target=scraping_task, args=(first_quarter, proxy))
thread2 = threading.Thread(target=scraping_task, args=(second_quarter, proxy))
thread3 = threading.Thread(target=scraping_task, args=(third_quarter, proxy))
thread4 = threading.Thread(target=scraping_task, args=(fourth_quarter, proxy))

start_time = time.time()  # Record the start time

# Starting threads
thread1.start()
thread2.start()
thread3.start()
thread4.start()

# Waiting for all threads to finish execution
thread1.join()
thread2.join()
thread3.join()
thread4.join()

print("\nAll table names have been successfully scraped.\n")
end_time = time.time()  # End time
elapsed_time_seconds = end_time - start_time
minutes = elapsed_time_seconds // 60
seconds = elapsed_time_seconds % 60
print(f"Total elapsed time: {minutes} minutes and {seconds} seconds.")


