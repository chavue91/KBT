import psycopg2
from app.db import get_connection

# ============================================================
# TRANSACTION DEMO — Batch Fish Submission
# ============================================================
# Scenario:
#   An angler submits multiple fish catches at once during a
#   tournament. Each fish is inserted individually with a
#   SAVEPOINT before it. If a single insert fails (bad length,
#   invalid species, etc.), we roll back to that savepoint and
#   skip that fish — without losing the ones that succeeded.
#   At the end we commit everything that passed.
#
# Angler:     Derek Holloway (user_id = 3)
# Tournament: Lake Minnetonka (tournament_id = 1)
# ============================================================

def submit_fish_batch(angler_user_id: int, tournament_id: int, catches: list):
    """
    Submits a batch of fish catches for an angler in a tournament.

    Each catch is a dict with keys:
        species     (str)
        fish_length (float)

    A SAVEPOINT is created before each insert. If an insert fails,
    we roll back to that savepoint and skip that fish. Valid catches
    are committed at the end.

    Args:
        angler_user_id: The user_id of the angler submitting catches.
        tournament_id:  The tournament the catches belong to.
        catches:        A list of dicts with species and fish_length.
    """
    conn = get_connection()
    if conn is None:
        print("  Could not connect to database.")
        return

    cursor = conn.cursor()

    try:
        # Look up the angler's livewell for this tournament
        cursor.execute("""
            SELECT lw.livewell_id
            FROM livewell lw
            JOIN tournament_anglers ta ON lw.tournament_entry_id = ta.tournament_angler_id
            WHERE ta.angler_user_id = %s AND ta.tournament_id = %s
        """, (angler_user_id, tournament_id))

        row = cursor.fetchone()
        if not row:
            print("  Error: no livewell found — is this angler registered for that tournament?")
            return

        livewell_id = row[0]
        successful  = []
        skipped     = []

        for i, catch in enumerate(catches, start=1):
            savepoint = f"before_fish_{i}"
            cursor.execute(f"SAVEPOINT {savepoint}")

            try:
                cursor.execute("""
                    INSERT INTO fish (livewell_id, species, fish_length, status)
                    VALUES (%s, %s, %s, 'PENDING')
                    RETURNING fish_id
                """, (livewell_id, catch["species"], catch["fish_length"]))

                fish_id = cursor.fetchone()[0]
                cursor.execute(f"RELEASE SAVEPOINT {savepoint}")
                successful.append({**catch, "fish_id": fish_id})
                print(f"  Fish {i}: accepted — {catch['species']} {catch['fish_length']}\" (fish_id={fish_id})")

            except psycopg2.Error as e:
                cursor.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
                cursor.execute(f"RELEASE SAVEPOINT {savepoint}")
                skipped.append({**catch, "reason": str(e).strip()})
                print(f"  Fish {i}: skipped — {catch['species']} {catch['fish_length']}\" — {e.pgcode}")

        # Commit all successful inserts
        conn.commit()

        print(f"\n  Batch complete.")
        print(f"  Committed: {len(successful)} fish")
        print(f"  Skipped:   {len(skipped)} fish")

        if skipped:
            print("\n  Skipped details:")
            for s in skipped:
                print(f"    - {s['species']} {s['fish_length']}\": {s['reason']}")

    except psycopg2.Error as e:
        conn.rollback()
        print(f"  Unexpected database error — full rollback: {e}")
    finally:
        cursor.close()
        conn.close()


# ============================================================
# DEMO ENTRY POINT
# ============================================================

if __name__ == "__main__":
    demo_catches = [
        {"species": "Largemouth Bass", "fish_length": 13.50},  # valid
        {"species": "Largemouth Bass", "fish_length": 150.00}, # invalid — exceeds 99.99 CHECK constraint
        {"species": "Smallmouth Bass", "fish_length": 11.25},  # valid
    ]

    print("\n  Running batch fish submission transaction demo...")
    print(f"  Angler user_id=3 | Tournament tournament_id=1")
    print(f"  Submitting {len(demo_catches)} catches...\n")

    submit_fish_batch(
        angler_user_id=3,
        tournament_id=1,
        catches=demo_catches
    )