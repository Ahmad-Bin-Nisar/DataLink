import psycopg2
import json

# Database connection setup
def get_db_connection():
    return psycopg2.connect(
        dbname="datalink_db", 
        user="datalink",      
        password="1234",      
        host="localhost",     
        port="5432"           
    )

# Function to insert data into PostgreSQL
def insert_data_from_json(json_file):
    conn = get_db_connection()
    cursor = conn.cursor()

    with open(json_file, 'r') as file:
        data = json.load(file)

    insert_query = """
        INSERT INTO system_metadata (parameter_name, parameter_value, last_updated)
        VALUES (%s, %s, %s)
    """

    for record in data:
        parameter_name = record['parameter_name']
        parameter_value = record['parameter_value']
        last_updated = record['last_updated']
        
        cursor.execute(insert_query, (parameter_name, parameter_value, last_updated))

    conn.commit()
    cursor.close()
    conn.close()

    print("Data inserted successfully!")

insert_data_from_json(r'E:\Bigdata_project\Datasets\system_metadata.json') 
