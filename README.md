# KBT - Kayak Bass Tournament
## Fishing Tournament Management System

KBT is a Python command-line application that manages kayak bass fishing tournaments using a hybrid database architecture — PostgreSQL for relational data and MongoDB for flexible fish photo documents.

---

## Project Structure

```
KBT/
│
├── app/
│   ├── __init__.py
│   ├── app.py               # CLI application — main entry point
│   ├── db.py                # PostgreSQL connection helper
│   └── transactions.py      # Transaction demo — batch fish submission
│
├── database/
│   ├── schema.sql           # PostgreSQL table definitions and indexes
│   ├── reset_db.sql         # Drops, recreates, and rebuilds PostgreSQL schema
│   ├── seed.sql             # (reserved)
│   ├── test_data.sql        # PostgreSQL test data population script
│   ├── queries.sql          # Reference queries (SELECT, JOIN, GROUP BY, subqueries, views)
│   └── transactions.sql     # SQL transaction demo with SAVEPOINT, ROLLBACK, COMMIT
│
├── mongo/
│   ├── __init__.py
│   ├── connection.py        # MongoDB connection helper (singleton)
│   ├── seed_fish_photos.py  # MongoDB seed script for fish_photos collection
│   └── models/
│       ├── __init__.py
│       └── fishPhoto.py     # CRUD operations for fish_photos collection
│
├── scripts/
│   ├── init_db.py
│   ├── test_db.py           # PostgreSQL connection test
│   ├── test_insert.py       # PostgreSQL insert test
│   ├── reset_mongo.py       # Resets MongoDB collections
│   └── reset_all.py         # Resets and reseeds both PostgreSQL and MongoDB
│
├── .env                     # DB credentials (NOT committed)
├── .env.example             # Example environment variables
├── requirements.txt         # Python dependencies
└── README.md
```

---

## Database Overview

### PostgreSQL — Relational

The schema models the following relationships:

- **Users** are the base entity. A user can be a Director, an Angler, or both.
- Each **Tournament** is managed by one Director.
- **Anglers** can participate in many tournaments, and tournaments can have many anglers.
- Each angler's participation in a tournament has exactly **one livewell**.
- A **livewell** holds many fish.
- Each **fish** has exactly one photo (stored in MongoDB).

Main tables:

| Table | Description |
|---|---|
| `users` | Base identity record for all people |
| `directors` | Specialization of users who manage tournaments |
| `anglers` | Specialization of users who compete |
| `tournaments` | Tournament events |
| `tournament_anglers` | Junction table — anglers registered for tournaments |
| `livewell` | One per tournament registration, holds fish |
| `fish` | Individual fish catches with status |
| `fish_photo` | Reference table — fish_id anchor for MongoDB photos |

### MongoDB — Non-Relational

Fish photos are stored in MongoDB in the `fish_photos` collection. Each document is linked to a PostgreSQL fish record via `fish_id`.

**Why MongoDB for fish photos?**

- Photo submissions carry varying metadata — GPS coordinates, camera specs, AI scoring hints, weather conditions, review notes, file info. This would require many nullable columns or extra tables in a rigid relational schema.
- Photo data grows fast and scales better horizontally in MongoDB.
- The `fish_photo` table in PostgreSQL is a simple anchor — no joins are needed on it. That's a natural fit for a document store.
- Storing documents in MongoDB makes it easy to extend photo metadata in the future without schema migrations.

**Document shape (varies per submission):**

```json
{
  "fish_id": 1,
  "photo_url": "https://storage.example.com/fish/fish-1.jpg",
  "uploaded_at": "2025-06-14T10:23:45Z",
  "gps": { "lat": 44.9211, "lon": -93.6702 },
  "camera": { "device": "iPhone 15 Pro", "resolution": "48MP" },
  "conditions": { "weather": "Sunny", "water_temp_f": 68.4 },
  "ai_score_hint": { "confidence": 0.97, "detected_species": "Largemouth Bass" }
}
```

---

## Starting the Databases

Both databases must be running before using the application or any scripts.

### PostgreSQL (WSL)

Check if PostgreSQL is running:
```bash
sudo service postgresql status
```

Start PostgreSQL:
```bash
sudo service postgresql start
```

Stop PostgreSQL:
```bash
sudo service postgresql stop
```

### MongoDB (Windows)

Open PowerShell as Administrator and run:

Check if MongoDB is running:
```powershell
Get-Service MongoDB
```

Start MongoDB:
```powershell
net start MongoDB
```

Stop MongoDB:
```powershell
net stop MongoDB
```

> **Note:** MongoDB must be started on Windows before running any scripts from WSL. You only need to do this once per session — it stays running until you stop it or restart Windows.

---

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd KBT
```

### 2. Create and activate a Python virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example file and fill in your credentials:

```bash
cp .env.example .env
```

Your `.env` should look like this:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=kbt
DB_USER=postgres
DB_PASSWORD=your_password

MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=kbt
```

> **WSL users:** MongoDB running on Windows is not accessible via `localhost` from WSL.
> Get your Windows host IP with `ip route show | grep -i default | awk '{ print $3}'`
> and use that as your `MONGO_URI` host instead.

### 5. Reset and reseed both databases

```bash
python scripts/reset_all.py
```

This will:
1. Drop and recreate the PostgreSQL `kbt` database
2. Rebuild the schema from `schema.sql`
3. Drop all MongoDB collections
4. Seed PostgreSQL with `test_data.sql`
5. Seed MongoDB with `seed_fish_photos.py`

---

## Running the Application

```bash
python -m app.app
```

---

## CLI Menu Reference

```
==================================================
   Fishing Tournament Management System
==================================================
  --- SELECT ---
  1. View all tournaments
  2. View all anglers
  3. View fish catches for a tournament
  4. View leaderboard for a tournament
  --- INSERT ---
  5. Add a new angler
  6. Register angler for a tournament
  7. Record a fish catch
  --- UPDATE ---
  8. Update fish catch status
  --- DELETE ---
  9. Remove angler from a tournament
  --- FISH PHOTOS (MongoDB) ---
  10. View photo for a fish
  11. Add photo for a fish
  12. Update photo URL for a fish
  13. Delete photo for a fish
  0. Exit
==================================================
```

---

## Demo Walkthrough

### Prerequisites

Make sure both databases are running and seeded:

```bash
python scripts/reset_all.py
```

---

### 1. View all tournaments

Select option `1`. Shows all three seeded tournaments with their director, location, and schedule.

---

### 2. View all anglers

Select option `2`. Shows all six seeded anglers with contact information.

---

### 3. View fish catches for a tournament

Select option `3`. Enter tournament ID `1`.

Shows all fish submitted by anglers in Tournament 1 (Lake Minnetonka) with species, length, and approval status.

---

### 4. View leaderboard for a tournament

Select option `4`. Enter tournament ID `1`.

Shows only APPROVED fish, ranked by total length. Demonstrates aggregate scoring logic.

---

### 5. Add a new angler

Select option `5`. Enter the following:

```
First name:    Demo
Last name:     Angler
Email:         demo.angler@email.com
Phone number:  (press Enter to skip)
```

Note the user ID returned — you will use it in the next step.

---

### 6. Register angler for a tournament

Select option `6`. Enter:

```
Angler user ID:  <ID returned from step 5>
Tournament ID:   1
```

This registers the angler and automatically creates their livewell for Tournament 1.

---

### 7. Record a fish catch

Select option `7`. Enter:

```
Angler user ID:  <ID from step 5>
Tournament ID:   1
Species:         Largemouth Bass
Fish length:     15.50
```

Note the fish ID returned — you will use it in the photo steps.

---

### 8. Update fish catch status

Select option `8`. Enter:

```
Fish ID:     <fish ID from step 7>
New status:  APPROVED
```

Re-run option `4` with tournament ID `1` to see the angler appear on the leaderboard.

---

### 9. Remove angler from a tournament

Select option `9`. Enter:

```
Angler user ID:  <ID from step 5>
Tournament ID:   1
```

Note: cascading delete removes their livewell and all fish records automatically.

---

### 10. View photo for a fish (MongoDB)

Select option `10`. Enter fish ID `1`.

Displays the full MongoDB document for that fish including any metadata fields present — GPS, camera, conditions, AI score hint.

---

### 11. Add photo for a fish (MongoDB)

Select option `11`. Enter:

```
Fish ID:    <fish ID from step 7>
Photo URL:  https://storage.example.com/fish/demo-fish.jpg
```

The business rule is enforced — if a photo already exists for that fish ID, the insert is blocked and you are directed to use option 12 instead.

---

### 12. Update photo URL for a fish (MongoDB)

Select option `12`. Enter:

```
Fish ID:        <fish ID from step 7>
New photo URL:  https://storage.example.com/fish/demo-fish-v2.jpg
```

The `uploaded_at` timestamp is updated automatically.

---

### 13. Delete photo for a fish (MongoDB)

Select option `13`. Enter:

```
Fish ID:  <fish ID from step 7>
```

The document is removed from the `fish_photos` collection.

---

### Transaction Demo — Batch Fish Submission

Run the transaction demo separately:

```bash
python -m app.transactions
```

**What it demonstrates:**

An angler submits 3 fish catches in a single batch. A `SAVEPOINT` is created before each insert. Fish 2 has an invalid length of 150.00 inches which violates the `CHECK` constraint (`fish_length` must be between 0.00 and 99.99).

**Expected output:**

```
  Running batch fish submission transaction demo...
  Angler user_id=3 | Tournament tournament_id=1
  Submitting 3 catches...

  Fish 1: accepted — Largemouth Bass 13.5" (fish_id=22)
  Fish 2: skipped — Largemouth Bass 150.0" — 23514
  Fish 3: accepted — Smallmouth Bass 11.25" (fish_id=23)

  Batch complete.
  Committed: 2 fish
  Skipped:   1 fish

  Skipped details:
    - Largemouth Bass 150.0": new row for relation "fish" violates check constraint "fish_fish_length_check"
```

**Key concept:** Without savepoints, Fish 2 failing would trigger a full rollback — Fish 1 would be lost too. Savepoints allow partial recovery within a single transaction. Fish 1 and Fish 3 are committed. Fish 2 is rolled back to its savepoint and skipped.

To also run the SQL version directly against the database:

```bash
psql -h localhost -p 5440 -U postgres -d kbt -f database/transactions.sql
```

---

## Technologies Used

- Python 3.10
- PostgreSQL 14
- MongoDB 8.0
- psycopg2
- pymongo
- python-dotenv
- prettytable
- Git / GitHub

---

## Authors

Cha Vue, Justin Halvorson