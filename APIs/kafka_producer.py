from kafka import KafkaProducer
import json
import time

# Setup Kafka producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Load the user interaction data
with open('E:/Bigdata_project/Datasets/5000000_user_interactions.json', 'r') as file:
    data = json.load(file)

print(f"Total interactions to send: {len(data)}")

# Send interactions to Kafka topic 'user_interactions'
for i, interaction in enumerate(data):
    try:
        producer.send('user_interactions', value=interaction)
        
        # Log progress every 10,000 messages
        if i % 10000 == 0:
            print(f"Sent {i} interactions...")

    except Exception as e:
        print(f"Error sending interaction {i}: {e}")

# Finalize
producer.flush()
producer.close()

print("All messages sent successfully.")


producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def publish_profile_update_event(event: dict):
    producer.send("user_profile_updates", value=event)
    producer.flush()
