from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl, EmailStr
from pymongo import MongoClient
from typing import List, Optional

app = FastAPI(title="LinkedIn Clone API")
MONGO_URI = "mongodb+srv://bigdata:Qwerty1234@cluster0.u7vhepp.mongodb.net/"

# ---------------------- MongoDB Setup ---------------------- #
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["linkedin_clone"]
mongo_profiles = mongo_db["user_profiles"]

# ---------------------- Data Model ---------------------- #
class UserProfile(BaseModel):
    user_id: str
    full_name: str
    email: EmailStr
    password: str
    location: str
    headline: str
    industry: str
    skills: List[str]
    experience: str
    profile_picture_url: Optional[HttpUrl] = None
    resume_url: Optional[HttpUrl] = None

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    about: Optional[str] = None
    connections: Optional[int] = None
    profile_views: Optional[int] = None
    experience: Optional[List[dict]] = None
    education: Optional[List[dict]] = None
    skills: Optional[List[str]] = None


# ---------------------- Create Profile ---------------------- #
@app.post("/api/user_profiles/")
def create_user_profile(profile: UserProfile):
    if mongo_profiles.find_one({"user_id": profile.user_id}):
        raise HTTPException(status_code=400, detail="User already exists")

    mongo_profiles.insert_one(profile.dict())
    return {"message": "User profile saved successfully"}

# ---------------------- Get Profile by ID ---------------------- #
@app.get("/api/user_profiles/{user_id}")
def get_user_profile(user_id: str):
    user = mongo_profiles.find_one({"user_id": user_id}, {"_id": 0})
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")

# ---------------------- Update Profile ---------------------- #
@app.put("/api/user_profiles/{user_id}")
def update_user_profile(user_id: str, updated: UserProfileUpdate):
    result = mongo_profiles.update_one(
        {"user_id": user_id},
        {"$set": {k: v for k, v in updated.dict().items() if v is not None}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User profile updated successfully"}


# ---------------------- Signup/Login Models ---------------------- #
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ExperienceEntry(BaseModel):
    title: str
    company: str
    duration: str
    description: str

class EducationEntry(BaseModel):
    school: str
    degree: str
    duration: str

class SignupRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str
    company: str
    location: str
    about: str
    experience: List[ExperienceEntry]
    education: List[EducationEntry]
    skills: List[str]

# ---------------------- Signup API ---------------------- #
@app.post("/api/auth/signup")
def signup_user(user: SignupRequest):
    if mongo_profiles.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists")

    user_id = "U" + str(mongo_profiles.estimated_document_count() + 1).zfill(6)

    profile = {
        "user_id": user_id,
        "full_name": user.full_name,
        "email": user.email,
        "password": user.password,
        "role": user.role,
        "company": user.company,
        "location": user.location,
        "about": user.about,
        "experience": [e.dict() for e in user.experience],
        "education": [e.dict() for e in user.education],
        "skills": user.skills,
        "connections": 0,
        "profile_views": 0
    }

    mongo_profiles.insert_one(profile)
    return {"message": "Signup successful", "user_id": user_id}

# ---------------------- Login API ---------------------- #
@app.post("/api/auth/login")
def login_user(credentials: LoginRequest):
    user = mongo_profiles.find_one({"email": credentials.email})
    if not user or user["password"] != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "message": "Login successful",
        "user_id": user["user_id"],
        "name": user["full_name"],
        'role': user["role"],
        'location': user["location"],
        'company': user["company"],
        'about': user["about"],
        'experience': user["experience"],
        'education': user["education"],
        'skills': user["skills"],
        'connections': user["connections"],
        'profile_views': user["profile_views"],
        'profile_picture_url': user.get("profile_picture_url"),
        'resume_url': user.get("resume_url")
    }

