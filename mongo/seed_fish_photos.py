"""
Seed script for fish_photos collection in MongoDB.

Mirrors the 11 fish photos inserted by test_data.sql (one per livewell,
first fish only). Documents intentionally carry varying metadata fields
to demonstrate the flexible document model advantage over a rigid
relational table.

Business Rules:
- Each fish has exactly one photo
- Species are restricted to Largemouth Bass or Smallmouth Bass

Fish IDs seeded: 1, 4, 6, 8, 9, 12, 14, 15, 17, 19, 20
"""

from datetime import datetime, timezone
from mongo.connection import get_mongo_db, close_mongo

COLLECTION = "fish_photos"

# Each document mirrors a fish from PostgreSQL via fish_id.
# Notice that documents do NOT all share the same shape:
#   - Some include GPS coordinates
#   - Some include camera/device metadata
#   - Some include AI scoring hints
#   - Some include weather and water conditions
#   - Some include review notes
#   - Some are minimal (basic submission only)
# This would require nullable columns or multiple tables in PostgreSQL.

SEED_DOCUMENTS = [
    {
        # fish_id 1 — Derek Holloway, T1 Lake Minnetonka, Largemouth Bass 14.50 APPROVED
        "fish_id": 1,
        "photo_url": "https://storage.example.com/fish/fish-1.jpg",
        "uploaded_at": datetime(2025, 6, 14, 10, 23, 45, tzinfo=timezone.utc),
        "gps": {"lat": 44.9211, "lon": -93.6702},
        "camera": {"device": "iPhone 15 Pro", "resolution": "48MP"},
        "conditions": {"weather": "Sunny", "water_temp_f": 68.4},
        "ai_score_hint": {"confidence": 0.97, "detected_species": "Largemouth Bass"}
    },
    {
        # fish_id 4 — Samantha Pike, T1 Lake Minnetonka, Largemouth Bass 16.25 APPROVED
        "fish_id": 4,
        "photo_url": "https://storage.example.com/fish/fish-4.jpg",
        "uploaded_at": datetime(2025, 6, 14, 9, 45, 12, tzinfo=timezone.utc),
        "camera": {"device": "Samsung Galaxy S24", "resolution": "200MP"},
        "ai_score_hint": {"confidence": 0.95, "detected_species": "Largemouth Bass"}
    },
    {
        # fish_id 6 — Carlos Vega, T1 Lake Minnetonka, Largemouth Bass 13.50 REJECTED
        # Minimal submission — photo was flagged during review
        "fish_id": 6,
        "photo_url": "https://storage.example.com/fish/fish-6.jpg",
        "uploaded_at": datetime(2025, 6, 14, 11, 5, 30, tzinfo=timezone.utc),
        "review_notes": "Measurement board not visible in photo."
    },
    {
        # fish_id 8 — Brenda Kowalski, T1 Lake Minnetonka, Largemouth Bass 15.00 APPROVED
        "fish_id": 8,
        "photo_url": "https://storage.example.com/fish/fish-8.jpg",
        "uploaded_at": datetime(2025, 6, 14, 8, 55, 0, tzinfo=timezone.utc),
        "gps": {"lat": 44.9198, "lon": -93.6811},
        "conditions": {"weather": "Partly Cloudy", "water_temp_f": 67.1},
        "file_info": {"size_kb": 2048, "format": "JPEG"}
    },
    {
        # fish_id 9 — Carlos Vega, T2 Mille Lacs Lake, Largemouth Bass 20.50 APPROVED
        "fish_id": 9,
        "photo_url": "https://storage.example.com/fish/fish-9.jpg",
        "uploaded_at": datetime(2025, 7, 19, 7, 30, 22, tzinfo=timezone.utc),
        "gps": {"lat": 46.2807, "lon": -93.6521},
        "camera": {"device": "GoPro Hero 12", "resolution": "27MP"},
        "conditions": {"weather": "Overcast", "water_temp_f": 72.0},
        "ai_score_hint": {"confidence": 0.99, "detected_species": "Largemouth Bass"},
        "file_info": {"size_kb": 4096, "format": "JPEG"}
    },
    {
        # fish_id 12 — Tom Braddock, T2 Mille Lacs Lake, Largemouth Bass 17.25 PENDING
        # Basic submission, still under review
        "fish_id": 12,
        "photo_url": "https://storage.example.com/fish/fish-12.jpg",
        "uploaded_at": datetime(2025, 7, 19, 8, 10, 5, tzinfo=timezone.utc),
        "file_info": {"size_kb": 1800, "format": "PNG"}
    },
    {
        # fish_id 14 — Nancy Elrod, T2 Mille Lacs Lake, Largemouth Bass 15.50 APPROVED
        "fish_id": 14,
        "photo_url": "https://storage.example.com/fish/fish-14.jpg",
        "uploaded_at": datetime(2025, 7, 19, 9, 0, 0, tzinfo=timezone.utc),
        "gps": {"lat": 46.3015, "lon": -93.7002},
        "ai_score_hint": {"confidence": 0.91, "detected_species": "Largemouth Bass"},
        "conditions": {"weather": "Sunny", "water_temp_f": 74.5}
    },
    {
        # fish_id 15 — Derek Holloway, T3 Lake Vermilion, Largemouth Bass 13.00 APPROVED
        "fish_id": 15,
        "photo_url": "https://storage.example.com/fish/fish-15.jpg",
        "uploaded_at": datetime(2025, 8, 2, 9, 15, 33, tzinfo=timezone.utc),
        "camera": {"device": "iPhone 15 Pro", "resolution": "48MP"},
        "gps": {"lat": 47.8310, "lon": -92.4869},
        "file_info": {"size_kb": 3100, "format": "JPEG"}
    },
    {
        # fish_id 17 — Brenda Kowalski, T3 Lake Vermilion, Smallmouth Bass 26.75 APPROVED
        "fish_id": 17,
        "photo_url": "https://storage.example.com/fish/fish-17.jpg",
        "uploaded_at": datetime(2025, 8, 2, 10, 44, 10, tzinfo=timezone.utc),
        "gps": {"lat": 47.8422, "lon": -92.4755},
        "camera": {"device": "Samsung Galaxy S24", "resolution": "200MP"},
        "conditions": {"weather": "Sunny", "water_temp_f": 71.8},
        "ai_score_hint": {"confidence": 0.98, "detected_species": "Smallmouth Bass"},
        "file_info": {"size_kb": 5200, "format": "JPEG"}
    },
    {
        # fish_id 19 — Tom Braddock, T3 Lake Vermilion, Largemouth Bass 14.00 PENDING
        # Minimal — quick submission from the water
        "fish_id": 19,
        "photo_url": "https://storage.example.com/fish/fish-19.jpg",
        "uploaded_at": datetime(2025, 8, 2, 11, 22, 0, tzinfo=timezone.utc),
    },
    {
        # fish_id 20 — Nancy Elrod, T3 Lake Vermilion, Smallmouth Bass 11.50 APPROVED
        "fish_id": 20,
        "photo_url": "https://storage.example.com/fish/fish-20.jpg",
        "uploaded_at": datetime(2025, 8, 2, 12, 5, 55, tzinfo=timezone.utc),
        "gps": {"lat": 47.8389, "lon": -92.4901},
        "conditions": {"weather": "Partly Cloudy", "water_temp_f": 70.3},
        "ai_score_hint": {"confidence": 0.93, "detected_species": "Smallmouth Bass"}
    }
]


def seed_fish_photos():
    db = get_mongo_db()
    collection = db[COLLECTION]

    # Clear existing data before seeding
    collection.drop()
    print(f"Dropped existing '{COLLECTION}' collection.")

    result = collection.insert_many(SEED_DOCUMENTS)
    print(f"Inserted {len(result.inserted_ids)} fish photo documents into '{COLLECTION}'.")


if __name__ == "__main__":
    try:
        seed_fish_photos()
    finally:
        close_mongo()