import pymongo
import json
import os

MONGO_URI = "mongodb+srv://bigdata:Qwerty1234@cluster0.u7vhepp.mongodb.net/"

def get_user_profiles_collection():
    client = pymongo.MongoClient(MONGO_URI)
    db = client["datalink"]  # Use the correct DB name you created
    collection_name = "user_profiles"

    if collection_name not in db.list_collection_names():
        db.create_collection(collection_name)
        print(f"✅ Collection '{collection_name}' created.")
    else:
        print(f"ℹ️ Collection '{collection_name}' already exists.")

    return db[collection_name]

def insert_user_data(json_path):
    collection = get_user_profiles_collection()

    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, list):
        collection.insert_many(data)
    else:
        collection.insert_one(data)

    print("✅ User profiles inserted successfully.")

def link_user_media(media_folder):
    collection = get_user_profiles_collection()

    for filename in os.listdir(media_folder):
        if not filename.startswith("U") or not os.path.isfile(os.path.join(media_folder, filename)):
            continue

        user_id = filename.split("_")[0]
        url_path = f"/user_media/{filename}"

        if "profile" in filename.lower():
            update = {"$set": {"profile_picture_url": url_path}}
        elif "resume" in filename.lower():
            update = {"$set": {"resume_url": url_path}}
        else:
            continue

        result = collection.update_one({"user_id": user_id}, update)
        if result.modified_count:
            print(f"✅ Linked media to {user_id}: {filename}")
        else:
            print(f"⚠️ No match found for {user_id}")

#if __name__ == "__main__":
    
    #insert_user_data(r"E:\Bigdata_project\1000_user_profiles.json")
    #link_user_media(r"E:\Bigdata_project\user_media")

if __name__ == "__main__":
    client = pymongo.MongoClient(MONGO_URI)
    db = client["datalink"]
    collection = db["user_profiles"]

    result = collection.update_many(
        {"password": {"$exists": False}},
        {"$set": {"password": "1234"}}
    )

    print(f"✅ Updated {result.modified_count} documents.")