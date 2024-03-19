import mysql.connector
from datetime import datetime, timedelta

# Database connection parameters
config = {
    'user': 'panagos',
    'password': 'password',
    'host': 'localhost',
    'database': 'mydatabase',
    'raise_on_warnings': True
}

# Connect to the MySQL database
conn = mysql.connector.connect(**config)
cursor = conn.cursor()

all_actions = ["Rent", "Buy"]
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

table_names = []
for action in all_actions:
    for city in all_cities:
        provinces = dict_cities_provinces.get(city)
        if provinces:
            table_names.extend([f"{action}_{city}_{province}" for province in provinces])
        else:
            table_names.append(f"{action}_{city}")

# Ensure the storage table exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS latest_tables_month (
    base_name VARCHAR(255),
    full_table_name VARCHAR(255)
)
""")

for base_name in table_names:
    found_tables = []
    date_to_check = datetime.now()
    
    for _ in range(30):  # Check for up to 30 days back
        table_suffix = date_to_check.strftime('_%d_%m_%Y')
        table_name_pattern = f"{base_name}{table_suffix}"
        
        # Check if table exists in the database
        cursor.execute(f"SHOW TABLES LIKE '{table_name_pattern}'")
        result = cursor.fetchall()
        
        if result:
            found_tables.append((base_name, table_name_pattern))
            if len(found_tables) >= 8:
                break  # Stop if 8 tables have been found
        
        date_to_check -= timedelta(days=1)  # Move to the previous day
    
    if not found_tables:
        cursor.execute("INSERT INTO latest_tables_month (base_name, full_table_name) VALUES (%s, %s)", (base_name, '0'))
    else:
        for base_name, full_table_name in found_tables:
            cursor.execute("INSERT INTO latest_tables_month (base_name, full_table_name) VALUES (%s, %s)", (base_name, full_table_name))
    
    conn.commit()

cursor.close()
conn.close()

print("Search completed and results saved to latest_tables_month.")
