from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
import uuid
import os

app = FastAPI(title="LinkedIn Clone API (Local Media Upload)")

UPLOAD_DIR = "E:/Bigdata_project/user_media"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/user_media", StaticFiles(directory=UPLOAD_DIR), name="user_media")

@app.post("/api/user_media/upload/")
async def upload_media(file: UploadFile = File(...)):
    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    return {
        "message": "File uploaded successfully!",
        "file_name": file.filename,
        "saved_as": filename,
        "url": f"http://127.0.0.1:8000/user_media/{filename}"
    }
