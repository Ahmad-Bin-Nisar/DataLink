from fastapi import FastAPI
import redis
import json

app = FastAPI(title="LinkedIn Clone API")

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@app.post("/api/session_cache/")
def cache_session(session_id: str, feed_data: dict):
    redis_client.set(session_id, json.dumps(feed_data), ex=3600)
    return {"message": "Session cached"}

@app.get("/api/session_cache/{session_id}")
def get_cached_session(session_id: str):
    data = redis_client.get(session_id)
    if not data:
        return {"message": "Session not found"}
    return json.loads(data)
