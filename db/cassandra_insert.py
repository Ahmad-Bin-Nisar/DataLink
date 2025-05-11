from cassandra.cluster import Cluster
from datetime import datetime
import random

# Connect to local Cassandra instance
cluster = Cluster(['127.0.0.1'], port=9042)
session = cluster.connect('datalink')

actions = ['profile_view', 'job_search', 'message_sent', 'post_created']

for i in range(10):
    user_id = f"U00000{i}"
    timestamp = datetime.now()
    action = random.choice(actions)

    session.execute("""
        INSERT INTO activity_logs (user_id, timestamp, action)
        VALUES (%s, %s, %s)
    """, (user_id, timestamp, action))

print(" 10 user activity logs inserted into Cassandra.")
