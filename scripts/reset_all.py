"""
reset_all.py

Resets and reseeds both PostgreSQL and MongoDB databases.

Order of operations:
    0. Preflight — verify both database connections are up
    1. Reset PostgreSQL  (drops and recreates kbt, runs schema.sql)
    2. Reset MongoDB     (drops all collections)
    3. Reseed PostgreSQL (runs test_data.sql)
    4. Reseed MongoDB    (runs seed_fish_photos)

Run from the project root:

    python -m scripts.reset_all
"""

import os
import subprocess
import psycopg2
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

from mongo.connection import get_mongo_db, close_mongo
from mongo.seed_fish_photos import seed_fish_photos

load_dotenv()

# ── PostgreSQL config ────────────────────────────────────────
DB_HOST     = os.getenv("DB_HOST")
DB_PORT     = os.getenv("DB_PORT", "5432")
DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME     = os.getenv("DB_NAME")

# ── MongoDB config ───────────────────────────────────────────
MONGO_URI     = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "kbt")

# ── MongoDB collections to reset ─────────────────────────────
COLLECTIONS = [
    "fish_photos"
]


# ============================================================
# PREFLIGHT CHECKS
# ============================================================

def check_postgres():
    """Verify PostgreSQL is reachable before doing anything."""
    print("  Checking PostgreSQL connection...")
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname="postgres",
            connect_timeout=5
        )
        conn.close()
        print("  PostgreSQL is up.")
        return True
    except psycopg2.OperationalError as e:
        print(f"  PostgreSQL is not reachable: {e}")
        print("  Start PostgreSQL with: sudo service postgresql start")
        return False


def check_mongo():
    """Verify MongoDB is reachable before doing anything."""
    print("  Checking MongoDB connection...")
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        client.close()
        print("  MongoDB is up.")
        return True
    except ConnectionFailure as e:
        print(f"  MongoDB is not reachable: {e}")
        print("  Start MongoDB on Windows with (admin PowerShell): net start MongoDB")
        return False


def preflight():
    """Run all preflight checks. Returns True only if all pass."""
    print("  Running preflight checks...\n")
    postgres_ok = check_postgres()
    mongo_ok    = check_mongo()

    if not postgres_ok or not mongo_ok:
        print("\n  Preflight failed — fix the above and try again.")
        return False

    print("\n  All systems go.\n")
    return True


# ============================================================
# POSTGRESQL HELPERS
# ============================================================

def run_sql_file(filepath: str):
    """Runs a SQL file against the PostgreSQL server using psql."""
    env = os.environ.copy()
    env["PGPASSWORD"] = DB_PASSWORD

    result = subprocess.run(
        [
            "psql",
            "-h", DB_HOST,
            "-p", DB_PORT,
            "-U", DB_USER,
            "-f", filepath
        ],
        env=env,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"  Error running {filepath}:")
        print(result.stderr)
        raise RuntimeError(f"psql failed on {filepath}")
    else:
        print(result.stdout)


def reset_postgres():
    print("  Resetting PostgreSQL...")
    run_sql_file("database/reset_db.sql")
    print("  PostgreSQL reset complete.")


def seed_postgres():
    print("  Seeding PostgreSQL...")
    run_sql_file("database/test_data.sql")
    print("  PostgreSQL seeded.")


# ============================================================
# MONGODB HELPERS
# ============================================================

def reset_mongo():
    print("  Resetting MongoDB...")
    db = get_mongo_db()
    for collection in COLLECTIONS:
        db[collection].drop()
        print(f"    Dropped collection: '{collection}'")
    print("  MongoDB reset complete.")


# ============================================================
# MAIN
# ============================================================

def main():
    print("\n" + "=" * 50)
    print("   Reset & Reseed — PostgreSQL + MongoDB")
    print("=" * 50 + "\n")

    # Step 0 — Preflight checks
    if not preflight():
        return

    try:
        # Step 1 — Reset PostgreSQL
        reset_postgres()
        print()

        # Step 2 — Reset MongoDB
        reset_mongo()
        print()

        # Step 3 — Reseed PostgreSQL
        seed_postgres()
        print()

        # Step 4 — Reseed MongoDB
        print("  Seeding MongoDB...")
        seed_fish_photos()
        print("  MongoDB seeded.")
        print()

        print("=" * 50)
        print("   All done. Both databases reset and reseeded.")
        print("=" * 50 + "\n")

    except Exception as e:
        print(f"\n  Failed: {e}")
    finally:
        close_mongo()


if __name__ == "__main__":
    main()