import mysql.connector

def get_db_config():
    """
    Prompt the user for database configuration details and return them as a dictionary.
    """
    host = input("Enter database host (e.g., 'localhost'): ")
    user = input("Enter database user: ")
    password = input("Enter database password: ")
    database = input("Enter database name: ")

    return {
        'host': host,
        'user': user,
        'password': password,
        'database': database
    }

def find_matching_tables(db_config, search_string):
    """
    Find and return table names containing the specified string.

    :param db_config: Dictionary containing MySQL connection parameters.
    :param search_string: String to search for in table names.
    :return: List of matching table names.
    """
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("SHOW TABLES")
        matching_tables = [table[0] for table in cursor.fetchall() if search_string in table[0]]

        print("Matching tables:", matching_tables)
        return matching_tables

    except mysql.connector.Error as err:
        print("Error occurred:", err)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def wipeDB(db_config):
    """
    Drop all tables from the database. This action is irreversible.
    """
    confirmation = input("Are you sure you want to wipe the database? This action cannot be undone. Type 'yes' to confirm: ")
    if confirmation.lower() != 'yes':
        print("Database wipe cancelled.")
        return

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]

        for table in tables:
            print(f"Dropping table {table}...")
            cursor.execute(f"DROP TABLE {table}")

        print("All tables have been dropped.")
    
    except mysql.connector.Error as err:
        print("Error occurred:", err)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def main():
    db_config = get_db_config()

    while True:
        print("\nMenu:")
        print("1. Find matching tables")
        print("2. Wipe database")
        print("3. Exit")

        choice = input("Enter your choice (1-3): ")

        if choice == '1':
            search_string = input("Enter search string for table names: ")
            find_matching_tables(db_config, search_string)
        elif choice == '2':
            yn = input("Are you sure you want to delete the WHOLE database? (Y/N): ")
            if yn=='Y':
                wipeDB(db_config)
        elif choice == '3':
            print("Exiting program.")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
