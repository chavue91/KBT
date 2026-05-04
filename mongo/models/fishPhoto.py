from datetime import datetime, timezone
from mongo.connection import get_mongo_db

COLLECTION = "fish_photos"

# Document shape (for reference — MongoDB does not enforce this):
# {
#   "fish_id":     int,   -- FK reference to PostgreSQL fish.fish_id
#   "photo_url":   str,   -- unique URL to stored image
#   "uploaded_at": datetime
# }


def get_collection():
    db = get_mongo_db()
    return db[COLLECTION]


# ── INSERT ──────────────────────────────────────────────────

def insert_fish_photo(fish_id: int, photo_url: str):
    collection = get_collection()
    doc = {
        "fish_id": fish_id,
        "photo_url": photo_url,
        "uploaded_at": datetime.now(timezone.utc)
    }
    result = collection.insert_one(doc)
    return result


# ── SELECT ──────────────────────────────────────────────────

def get_fish_photo_by_fish_id(fish_id: int):
    collection = get_collection()
    return collection.find_one({"fish_id": fish_id})


def get_all_fish_photos():
    collection = get_collection()
    return list(collection.find({}))


# ── UPDATE ──────────────────────────────────────────────────

def update_fish_photo_url(fish_id: int, new_photo_url: str):
    collection = get_collection()
    result = collection.update_one(
        {"fish_id": fish_id},
        {"$set": {
            "photo_url": new_photo_url,
            "uploaded_at": datetime.now(timezone.utc)
        }}
    )
    return result


# ── DELETE ──────────────────────────────────────────────────

def delete_fish_photo(fish_id: int):
    collection = get_collection()
    result = collection.delete_one({"fish_id": fish_id})
    return result