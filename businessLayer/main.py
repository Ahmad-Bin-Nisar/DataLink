from fastapi import FastAPI, Request
from kafka_producer import publish_event
from db.mongo import insert_user_profile
from db.cassandra import insert_interaction
from db.redis import cache_feed

app = FastAPI()

@app.get("/")
def read_root():
    return {"msg": "Backend API is running"}

@app.post("/profile")
async def update_profile(payload: dict):
    insert_user_profile(payload)        
    await publish_event("profile_update", payload)  
    return {"status": "profile updated"}

@app.post("/interaction")
async def record_interaction(payload: dict):
    insert_interaction(payload)           
    await publish_event("interaction", payload)  
    return {"status": "interaction recorded"}

@app.post("/cache_feed")
def cache_user_feed(payload: dict):
    user_id = payload["user_id"]
    posts = payload["posts"]
    cache_feed(user_id, posts)           
    return {"status": "feed cached"}
