import mysql.connector
import numpy as np
import re  # For regex matching

# Connection configuration
config = {
    'user': 'panagos',
    'password': 'password',
    'host': 'localhost',
    'database': 'mydatabase'
}

def process_table(cnx, table_name):
    cursor = cnx.cursor()
    print(f"Processing table: {table_name}")

    # Fetch the data
    cursor.execute(f"SELECT id, size, price FROM {table_name}")
    rows = cursor.fetchall()

    # Calculate price/size value for each row, ensuring numerical division
    ratios = np.array([float(row[2])/float(row[1]) for row in rows])

    # Identify outliers using IQR
    q1, q3 = np.percentile(ratios, [25, 75])
    iqr = q3 - q1
    lower_bound = q1 - (1.5 * iqr)
    upper_bound = q3 + (1.5 * iqr)
    
    # Filtering outliers
    outliers = [rows[i][0] for i in range(len(rows)) if ratios[i] < lower_bound or ratios[i] > upper_bound]
    
    # Print and delete outliers
    if outliers:
        print("Deleting outliers:")
        for outlier_id in outliers:
            cursor.execute(f"DELETE FROM {table_name} WHERE id = {outlier_id}")
        cnx.commit()
        print(f"{len(outliers)} outliers deleted.")
    else:
        print("No outliers found.")

    # Recalculate the ppm value based on the updated data
    cursor.execute(f"SELECT SUM(price), SUM(size) FROM {table_name}")
    total_price, total_size = cursor.fetchone()
    new_ppm = total_price / total_size
    
    # Round the new ppm value to two decimal places
    new_ppm_rounded = round(new_ppm, 2)
    
    # Update the ppm value for all rows with the rounded value
    cursor.execute(f"UPDATE {table_name} SET ppm = {new_ppm_rounded}")
    cnx.commit()
    print(f"All ppm values updated to {new_ppm_rounded}.")

    cursor.close()

def delete_outliers_for_all_numbered_tables():
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        
        # Fetch all table names in the database
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        # Filter tables that end with a number
        table_names = [table[0] for table in tables if re.search(r'\d$', table[0])]

        for table_name in table_names:
            process_table(cnx, table_name)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cnx.is_connected():
            cursor.close()
            cnx.close()

# Execute the function to process all relevant tables
delete_outliers_for_all_numbered_tables()
