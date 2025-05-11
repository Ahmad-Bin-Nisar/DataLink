from cassandra.cluster import Cluster
from collections import defaultdict

cluster = Cluster(['127.0.0.1'], port=9042)
session = cluster.connect('datalink')

print("🔍 Fetching user interactions from Cassandra...")

rows = session.execute("SELECT user_id FROM user_interactions")

counter = defaultdict(int)
for row in rows:
    counter[row.user_id] += 1

top_users = sorted(counter.items(), key=lambda x: x[1], reverse=True)[:20]

print("\n🏆 Top 10 Most Active Users:")
for rank, (user_id, count) in enumerate(top_users, start=1):
    print(f"{rank}. {user_id}: {count} interactions")

cluster.shutdown()
print("✅ Cassandra connection closed.")