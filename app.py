from flask import Flask, jsonify, request
import mysql.connector
from flask_cors import CORS
from mysql.connector import Error
from datetime import datetime, timedelta
import math


app = Flask(__name__)
CORS(app)  # Enable CORS

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'panagos',
    'password': 'password',
    'database': 'mydatabase'
}

@app.route('/latest_tables_month/<table_name>')
def get_latest_tables(table_name):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "SELECT full_table_name FROM latest_tables_month WHERE base_name = %s"
        cursor.execute(query, (table_name,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not rows:
            return jsonify({'message': 'No tables found for the given base name'}), 404

        return [row[0] for row in rows]
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/latest_tables/<table_name>')
def get_latest_table_name(table_name):
    conn = mysql.connector.connect(**db_config)
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT full_table_name FROM latest_tables
            WHERE table_name = %s
        """, (table_name,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            return result[0]
        else:
            return jsonify({'error': 'Table not found'}), 404
    else:
        return jsonify({'error': 'Failed to connect to the database'}), 500
    

@app.route('/api/cities_hierarchy', methods=['GET'])
def get_cities():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM cities_hierarchy"
    cursor.execute(query)
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    # Format the result as needed
    formatted_result = {}
    for row in result:
        parent = row['parent']
        place = row['place']
        if parent not in formatted_result:
            formatted_result[parent] = []
        formatted_result[parent].append(place)

    return jsonify(formatted_result)


@app.route('/data', methods=['GET'])
def handle_data():
    # Connect to the database
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(dictionary=True)

    try:
        if request.method == 'GET':
            table_name = request.args.get('table')
            query = f"SELECT * FROM {table_name}"
            cursor.execute(query)
            results = cursor.fetchall()
            return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        cnx.close()


def get_table_names_for_base_name(base_name):
    table_names = []
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "SELECT full_table_name FROM latest_tables_month WHERE base_name = %s"
        cursor.execute(query, (base_name,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if rows:
            table_names = [row[0] for row in rows]
    except Exception as e:
        print(f"Error retrieving table names for base name {base_name}: {e}")
    return table_names

@app.route('/last_month_prices/<table_name>/<int:size>')
def last_month_prices(table_name, size):
    results = []
    try:
        table_names = get_table_names_for_base_name(table_name)
        if not table_names:
            return jsonify({'message': 'No tables found for the given base name'}), 404

        for table in table_names:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            # Query to find the closest size within ±5 square meters, preferring smaller if equidistant
            query = f"SELECT size, price FROM {table} WHERE ABS(size - %s) <= 5 ORDER BY ABS(size - %s), size ASC LIMIT 1"
            cursor.execute(query, (size, size))
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result:
                # Extract the date from the table name
                date_part = table.split('_')[-3:]  # Assuming the format '_dd_mm_yyyy'
                formatted_date = '-'.join(date_part)  # Convert to 'dd-mm-yyyy'
                # formatted_date = '-'.join([date_part[1], date_part[0], date_part[2]])  # Convert to 'mm-dd-yyyy'

                # Append the result along with the formatted date to results list
                results.append({
                    'date': formatted_date,
                    'size': result['size'],
                    'price': result['price']
                })

        if not results:
            return jsonify({'message': 'No suitable size found within ±5 square meters for any table'}), 404
        
        return jsonify(results[::-1]) # !!Reversed data!!
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
