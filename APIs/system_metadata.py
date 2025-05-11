from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
import requests

app = FastAPI(title="LinkedIn Clone API")

pg_conn = psycopg2.connect(
    dbname="linkedin_clone", user="postgres", password="yourpassword", host="localhost"
)
pg_cursor = pg_conn.cursor()

class SystemMetadata(BaseModel):
    config_id: str
    parameter_name: str

@app.post("/api/system_metadata/")
def save_metadata(metadata: SystemMetadata):
    pg_cursor.execute(
        "INSERT INTO system_metadata (config_id, parameter_name) VALUES (%s, %s)",
        (metadata.config_id, metadata.parameter_name)
    )
    pg_conn.commit()

    nifi_url = "http://localhost:8080/nifi-api/data"
    try:
        requests.post(nifi_url, json=metadata.dict())
    except Exception as e:
        return {"warning": "Metadata saved but not sent to NiFi", "error": str(e)}

    return {"message": "Metadata saved and sent to NiFi"}