from cassandra.cluster import Cluster
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import pandas as pd

# Connect to Cassandra
cluster = Cluster(['127.0.0.1'], port=9042)
session = cluster.connect('datalink')

print("Fetching user interactions for time-based analysis...")

rows = session.execute("SELECT timestamp, action FROM user_interactions")

# Count interactions per day and action
daily_counts = defaultdict(int)
daily_actions = defaultdict(lambda: Counter())

for row in rows:
    if row.timestamp:
        date_str = row.timestamp.date().isoformat()
        daily_counts[date_str] += 1
        daily_actions[date_str][row.action] += 1

date_series = pd.Series(daily_counts).sort_index()
action_df = pd.DataFrame(daily_actions).T.fillna(0).astype(int).sort_index()

# Plot: Total Interactions Per Day
plt.figure(figsize=(10, 5))
date_series.plot(kind='line', marker='o', color='blue')
plt.title("Total Interactions Per Day")
plt.xlabel("Date")
plt.ylabel("Interaction Count")
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.savefig("interactions_per_day.png")
print("Saved: interactions_per_day.png")

# Plot: Action Type Breakdown Per Day (Stacked Bar)
action_df.plot(kind='bar', stacked=True, figsize=(12, 6), colormap='Set2')
plt.title("Action Type Breakdown Per Day")
plt.xlabel("Date")
plt.ylabel("Interaction Count")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("interaction_types_per_day.png")
print("Saved: interaction_types_per_day.png")

cluster.shutdown()
print("Cassandra connection closed.")
