
import mysql.connector

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
                        "Thessaloniki": ["Municipality", "RegionalMunicipality", "DistrictRest", "40Ekklisies", "AgiaSofia", "AgiosAthanasios", "AgiosGeorgios", "AgiosPavlos", "Ampelokipoi", "Analipsi", "Antigonidon", "AnoPoli", "Axios", "Apollonia", "Arethousa"]
                        }

# MySQL connection details
db_config = {
    "host": "localhost",
    "user": "panagos",
    "password": "password",
    "database": "mydatabase"
}

# Connect to the MySQL database
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# SQL to create the table
cursor.execute("""
CREATE TABLE IF NOT EXISTS cities_hierarchy (
    parent VARCHAR(255),
    place VARCHAR(255)
)
""")

# Insert data
for city in all_cities:
    if city in dict_cities_provinces:
        for province in dict_cities_provinces[city]:
            cursor.execute("INSERT INTO cities_hierarchy (parent, place) VALUES (%s, %s)", (city, province))
    else:
        cursor.execute("INSERT INTO cities_hierarchy (parent, place) VALUES ('City', %s)", (city,))

# Commit changes and close connection
conn.commit()
cursor.close()
conn.close()
