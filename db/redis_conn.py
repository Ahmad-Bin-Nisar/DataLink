import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

with open(r'E:\Bigdata_project\1000_user_profiles.json', 'r') as file:
    users = json.load(file)

for user in users:
    user_id = user.get('user_id')
    redis_client.set(user_id, json.dumps(user))

print("All user profiles have been stored in Redis.")
