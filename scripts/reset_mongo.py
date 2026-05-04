"""
reset_mongo.py

Resets the MongoDB kbt database by dropping all collections.
Run this from the project root:

    python scripts/reset_mongo.py
"""

from mongo.connection import get_mongo_db, close_mongo

COLLECTIONS = [
    "fish_photos"
]


def reset_mongo():
    db = get_mongo_db()

    print(f"  Resetting MongoDB database: '{db.name}'")

    for collection in COLLECTIONS:
        db[collection].drop()
        print(f"  Dropped collection: '{collection}'")

    print("  MongoDB reset complete.")


if __name__ == "__main__":
    try:
        reset_mongo()
    finally:
        close_mongo()