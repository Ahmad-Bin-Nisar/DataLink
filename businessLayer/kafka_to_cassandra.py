from confluent_kafka import Consumer
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
import json
from uuid import uuid4
from datetime import datetime

# Kafka consumer config
kafka_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'interaction-consumer-group',
    'auto.offset.reset': 'earliest'
}
consumer = Consumer(kafka_config)
consumer.subscribe(['user_interactions'])

# Cassandra config
cluster = Cluster(['127.0.0.1'], port=9042)
session = cluster.connect('datalink')

insert_query = session.prepare("""
    INSERT INTO user_interactions (user_id, timestamp, interaction_id, action, target_id)
    VALUES (?, ?, ?, ?, ?)
""")

print("Kafka → Cassandra consumer is now listening...")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Kafka error: {msg.error()}")
            continue

        try:
            record = json.loads(msg.value().decode('utf-8'))

            print("Received record:", record)

            required_fields = ['user_id', 'timestamp', 'action_type']
            if not all(field in record for field in required_fields):
                print(f"Skipped malformed record: {record}")
                continue

            # Parse timestamp
            try:
                ts = datetime.fromisoformat(record['timestamp'])
            except Exception:
                print(f"Invalid timestamp format: {record['timestamp']}")
                continue

            session.execute(insert_query, (
                record['user_id'],
                ts,
                uuid4(),
                record['action_type'],
                record.get('target_id', '')
            ))

            print(f"Inserted: {record['user_id']} | {record['action_type']}")

        except Exception as e:
            print(f"Insert failed: {e}")

except KeyboardInterrupt:
    print("Stopping consumer...")
finally:
    consumer.close()
    cluster.shutdown()
    print("Kafka consumer closed and Cassandra connection shut down.")
