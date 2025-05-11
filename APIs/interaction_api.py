from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cassandra.cluster import Cluster
from uuid import uuid4
from datetime import datetime

cluster = Cluster(['127.0.0.1'], port=9042)
session = cluster.connect('datalink')
app = FastAPI(title="User Interaction API")

class Interaction(BaseModel):
    user_id: str
    action_type: str
    target_id: str = ""
    timestamp: datetime = datetime.utcnow()

# --- Create interaction ---
@app.post("/api/interactions/")
def create_interaction(interaction: Interaction):
    insert_query = session.prepare("""
        INSERT INTO user_interactions (user_id, timestamp, interaction_id, action, target_id)
        VALUES (?, ?, ?, ?, ?)
    """)
    session.execute(insert_query, (
        interaction.user_id,
        interaction.timestamp,
        uuid4(),
        interaction.action_type,
        interaction.target_id
    ))
    return {"message": "✅ Interaction added successfully"}

# --- Get interactions by user ---
@app.get("/api/interactions/{user_id}")
def get_interactions(user_id: str):
    try:
        query = f"SELECT * FROM user_interactions WHERE user_id = %s LIMIT 50"
        rows = session.execute(query, (user_id,))
        interactions = [
            {
                "user_id": row.user_id,
                "timestamp": row.timestamp.isoformat(),
                "interaction_id": str(row.interaction_id),
                "action": row.action,
                "target_id": row.target_id
            } for row in rows
        ]
        return interactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
