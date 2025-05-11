from cassandra.cluster import Cluster
import pandas as pd
import matplotlib.pyplot as plt

# Connect to Cassandra keyspace
cluster = Cluster(['127.0.0.1'])
session = cluster.connect('datalink')

rows = session.execute("SELECT action FROM activity_logs")

action_counts = {}
for row in rows:
    action = row.action
    action_counts[action] = action_counts.get(action, 0) + 1

df = pd.DataFrame(list(action_counts.items()), columns=["Action", "Count"])

df.plot(kind='bar', x='Action', y='Count', legend=False, title="User Interactions Count")
plt.xlabel("Interaction Type")
plt.ylabel("Frequency")
plt.tight_layout()
plt.show()
