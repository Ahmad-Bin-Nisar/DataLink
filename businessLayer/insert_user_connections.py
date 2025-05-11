import psycopg2
import json

# Database connection
def get_db_connection():
    return psycopg2.connect(
        dbname="datalink_db",
        user="datalink",
        password="1234",
        host="localhost",
        port="5432"
    )

# Function to insert user connections
def insert_user_connections(json_file):
    conn = get_db_connection()
    cursor = conn.cursor()

    with open(json_file, "r") as file:
        data = json.load(file)

    insert_query = """
        INSERT INTO user_connections (connection_id, user_id_1, user_id_2, connected_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (connection_id) DO NOTHING
    """

    for conn_record in data:
        cursor.execute(insert_query, (
            conn_record["connection_id"],
            conn_record["user_id_1"],
            conn_record["user_id_2"],
            conn_record["connected_at"]
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ User connections inserted successfully.")

# Run
if __name__ == "__main__":
    insert_user_connections(r"E:\Bigdata_project\Datasets\3000000_user_connections.json")
