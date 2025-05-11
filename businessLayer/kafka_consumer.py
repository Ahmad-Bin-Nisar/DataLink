from kafka import KafkaConsumer
import json
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from datetime import datetime

# Connect to Kafka
consumer = KafkaConsumer(
    'user_interactions',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='interaction-group'
)

# Connect to Cassandra
cluster = Cluster(['127.0.0.1'])
session = cluster.connect('datalink')

insert_query = SimpleStatement("""
    INSERT INTO activity_logs (user_id, timestamp, action)
    VALUES (%s, %s, %s)
""")

print("Listening to Kafka topic 'user_interactions'...")

for message in consumer:
    data = message.value
    try:
        user_id = data['user_id']
        timestamp = datetime.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S')
        action = data['action_type']
        session.execute(insert_query, (user_id, timestamp, action))
        print(f"Inserted interaction: {user_id} - {action}")
    except Exception as e:
        print("Error processing message:", e)
