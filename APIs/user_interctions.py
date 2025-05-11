import json
from time import sleep
from confluent_kafka import Producer

# Kafka Configuration
kafka_config = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'interaction-batch-producer'
}
producer = Producer(kafka_config)
TOPIC = 'user_interactions'

def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(f"Sent: {msg.value().decode('utf-8')}")

# Load and push interactions
def send_interactions_to_kafka(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    print(f"Total interactions to send: {len(data)}")

    for record in data:
        producer.produce(TOPIC, value=json.dumps(record), callback=delivery_report)
        sleep(0.001)

    producer.flush()
    print("All interactions sent to Kafka.")

if __name__ == "__main__":
    send_interactions_to_kafka(r"E:\Bigdata_project\Datasets\5000000_user_interactions.json")
    print("Kafka producer is running...")
