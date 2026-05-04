import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "kbt")

_client = None
_db = None


def get_mongo_db():
    global _client, _db

    if _db is not None:
        return _db

    try:
        _client = MongoClient(MONGO_URI)
        _client.admin.command("ping")
        _db = _client[MONGO_DB_NAME]
        print(f"Connected to MongoDB — database: {MONGO_DB_NAME}")
        return _db
    except ConnectionFailure as e:
        print(f"Could not connect to MongoDB: {e}")
        raise


def close_mongo():
    global _client, _db

    if _client is not None:
        _client.close()
        _client = None
        _db = None
        print("MongoDB connection closed.")