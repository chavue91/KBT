import psycopg2
from psycopg2 import OperationalError, errorcodes, errors
from prettytable import PrettyTable
from dotenv import load_dotenv
import os

load_dotenv()

# ============================================================
# CONNECTION
# ============================================================

def get_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            dbname=os.getenv("DB_NAME"),
            port=os.getenv("DB_PORT", 5432)
        )
        return conn
    except OperationalError as e:
        print(f"  Could not connect to database: {e}")
        return None


# ============================================================
# DISPLAY HELPER
# ============================================================

def print_result(cursor):
    rows = cursor.fetchall()
    if not rows:
        print("  No results found.")
        return
    table = PrettyTable()
    table.field_names = [desc[0] for desc in cursor.description]
    table.add_rows(rows)
    print(table)


# ============================================================
# MENU
# ============================================================

def print_menu():
    print("\n" + "=" * 50)
    print("   Fishing Tournament Management System")
    print("=" * 50)
    print("  --- SELECT ---")
    print("  1. View all tournaments")
    print("  2. View all anglers")
    print("  3. View fish catches for a tournament")
    print("  4. View leaderboard for a tournament")
    print("  --- INSERT ---")
    print("  5. Add a new angler")
    print("  6. Register angler for a tournament")
    print("  7. Record a fish catch")
    print("  --- UPDATE ---")
    print("  8. Update fish catch status")
    print("  --- DELETE ---")
    print("  9. Remove angler from a tournament")
    print("  0. Exit")
    print("=" * 50)


# ============================================================
# SELECT OPERATIONS
# ============================================================

def view_all_tournaments(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT t.tournament_id, u.first_name || ' ' || u.last_name AS director,
                   t.body_of_water, t.city, t.state_code,
                   t.tournament_date, t.start_time, t.end_time
            FROM tournaments t
            JOIN users u ON t.director_user_id = u.user_id
            ORDER BY t.tournament_date
        """)
        print_result(cursor)
    except psycopg2.Error as e:
        print(f"  Database error: {e}")
    finally:
        cursor.close()


def view_all_anglers(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT u.user_id, u.first_name, u.last_name, u.email, u.phone_number
            FROM users u
            JOIN anglers a ON u.user_id = a.user_id
            ORDER BY u.last_name
        """)
        print_result(cursor)
    except psycopg2.Error as e:
        print(f"  Database error: {e}")
    finally:
        cursor.close()


def view_fish_by_tournament(conn):
    cursor = conn.cursor()
    try:
        tournament_id = int(input("  Enter tournament ID: ").strip())
        cursor.execute("""
            SELECT u.first_name || ' ' || u.last_name AS angler,
                   f.fish_id, f.species, f.fish_length, f.status
            FROM fish f
            JOIN livewell lw ON f.livewell_id = lw.livewell_id
            JOIN tournament_anglers ta ON lw.tournament_entry_id = ta.tournament_angler_id
            JOIN users u ON ta.angler_user_id = u.user_id
            WHERE ta.tournament_id = %s
            ORDER BY u.last_name, f.fish_length DESC
        """, (tournament_id,))
        print_result(cursor)
    except ValueError:
        print("  Invalid input — tournament ID must be a number.")
    except psycopg2.Error as e:
        print(f"  Database error: {e}")
    finally:
        cursor.close()


def view_leaderboard(conn):
    cursor = conn.cursor()
    try:
        tournament_id = int(input("  Enter tournament ID: ").strip())
        cursor.execute("""
            SELECT u.first_name || ' ' || u.last_name AS angler,
                   COUNT(f.fish_id) AS approved_fish,
                   SUM(f.fish_length) AS total_length_inches
            FROM fish f
            JOIN livewell lw ON f.livewell_id = lw.livewell_id
            JOIN tournament_anglers ta ON lw.tournament_entry_id = ta.tournament_angler_id
            JOIN users u ON ta.angler_user_id = u.user_id
            WHERE ta.tournament_id = %s AND f.status = 'APPROVED'
            GROUP BY u.user_id, u.first_name, u.last_name
            ORDER BY total_length_inches DESC
        """, (tournament_id,))
        print_result(cursor)
    except ValueError:
        print("  Invalid input — tournament ID must be a number.")
    except psycopg2.Error as e:
        print(f"  Database error: {e}")
    finally:
        cursor.close()


# ============================================================
# INSERT OPERATIONS
# ============================================================

def add_angler(conn):
    cursor = conn.cursor()
    try:
        first_name   = input("  First name: ").strip()
        last_name    = input("  Last name: ").strip()
        email        = input("  Email: ").strip()
        phone_number = input("  Phone number (optional, press Enter to skip): ").strip() or None

        # Insert into users then anglers using RETURNING
        cursor.execute("""
            WITH new_user AS (
                INSERT INTO users (first_name, last_name, email, phone_number)
                VALUES (%s, %s, %s, %s)
                RETURNING user_id
            )
            INSERT INTO anglers (user_id)
            SELECT user_id FROM new_user
            RETURNING user_id
        """, (first_name, last_name, email, phone_number))

        new_id = cursor.fetchone()[0]
        conn.commit()
        print(f"  Angler added successfully with user ID {new_id}.")

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        print("  Error: that email address is already registered.")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"  Database error: {e}")
    finally:
        cursor.close()


def register_angler_for_tournament(conn):
    cursor = conn.cursor()
    try:
        angler_id     = int(input("  Enter angler user ID: ").strip())
        tournament_id = int(input("  Enter tournament ID: ").strip())

        # Register in tournament_anglers then create their livewell
        cursor.execute("""
            WITH new_entry AS (
                INSERT INTO tournament_anglers (tournament_id, angler_user_id)
                VALUES (%s, %s)
                RETURNING tournament_angler_id
            )
            INSERT INTO livewell (tournament_entry_id)
            SELECT tournament_angler_id FROM new_entry
        """, (tournament_id, angler_id))

        conn.commit()
        print(f"  Angler {angler_id} registered for tournament {tournament_id} and livewell created.")

    except ValueError:
        print("  Invalid input — IDs must be numbers.")
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        print("  Error: that angler is already registered for this tournament.")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"  Database error: {e}")
    finally:
        cursor.close()


def record_fish_catch(conn):
    cursor = conn.cursor()
    try:
        angler_id     = int(input("  Enter angler user ID: ").strip())
        tournament_id = int(input("  Enter tournament ID: ").strip())
        species       = input("  Species: ").strip()
        fish_length   = float(input("  Fish length (inches): ").strip())

        # Look up the livewell for this tournament entry
        cursor.execute("""
            SELECT lw.livewell_id
            FROM livewell lw
            JOIN tournament_anglers ta ON lw.tournament_entry_id = ta.tournament_angler_id
            WHERE ta.angler_user_id = %s AND ta.tournament_id = %s
        """, (angler_id, tournament_id))

        row = cursor.fetchone()
        if not row:
            print("  Error: no livewell found — is this angler registered for that tournament?")
            return

        livewell_id = row[0]
        cursor.execute("""
            INSERT INTO fish (livewell_id, species, fish_length, status)
            VALUES (%s, %s, %s, 'PENDING')
            RETURNING fish_id
        """, (livewell_id, species, fish_length))

        fish_id = cursor.fetchone()[0]
        conn.commit()
        print(f"  Fish recorded successfully with fish ID {fish_id} (status: PENDING).")

    except ValueError:
        print("  Invalid input — IDs and length must be numbers.")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"  Database error: {e}")
    finally:
        cursor.close()


# ============================================================
# UPDATE OPERATION
# ============================================================

def update_fish_status(conn):
    cursor = conn.cursor()
    valid_statuses = {"APPROVED", "REJECTED", "PENDING"}
    try:
        fish_id    = int(input("  Enter fish ID: ").strip())
        new_status = input("  New status (APPROVED / REJECTED / PENDING): ").strip().upper()

        if new_status not in valid_statuses:
            print("  Invalid status. Must be APPROVED, REJECTED, or PENDING.")
            return

        cursor.execute("""
            UPDATE fish SET status = %s WHERE fish_id = %s
        """, (new_status, fish_id))

        if cursor.rowcount == 0:
            print(f"  No fish found with ID {fish_id}.")
        else:
            conn.commit()
            print(f"  Fish {fish_id} status updated to {new_status}.")

    except ValueError:
        print("  Invalid input — fish ID must be a number.")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"  Database error: {e}")
    finally:
        cursor.close()


# ============================================================
# DELETE OPERATION
# ============================================================

def remove_angler_from_tournament(conn):
    cursor = conn.cursor()
    try:
        angler_id     = int(input("  Enter angler user ID: ").strip())
        tournament_id = int(input("  Enter tournament ID: ").strip())

        cursor.execute("""
            SELECT tournament_angler_id FROM tournament_anglers
            WHERE angler_user_id = %s AND tournament_id = %s
        """, (angler_id, tournament_id))

        if not cursor.fetchone():
            print("  No registration found for that angler and tournament.")
            return

        # Cascading delete will also remove livewell and fish records
        cursor.execute("""
            DELETE FROM tournament_anglers
            WHERE angler_user_id = %s AND tournament_id = %s
        """, (angler_id, tournament_id))

        conn.commit()
        print(f"  Angler {angler_id} removed from tournament {tournament_id}.")
        print("  Note: all associated livewell and fish records were also removed.")

    except ValueError:
        print("  Invalid input — IDs must be numbers.")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"  Database error: {e}")
    finally:
        cursor.close()


# ============================================================
# MAIN
# ============================================================

def main():
    conn = get_connection()
    if conn is None:
        print("  Exiting — could not establish a database connection.")
        return

    print("\n  Connected to Fishing Tournament database.")

    menu_options = {
        "1": view_all_tournaments,
        "2": view_all_anglers,
        "3": view_fish_by_tournament,
        "4": view_leaderboard,
        "5": add_angler,
        "6": register_angler_for_tournament,
        "7": record_fish_catch,
        "8": update_fish_status,
        "9": remove_angler_from_tournament,
    }

    while True:
        print_menu()
        choice = input("  Enter your choice: ").strip()

        if choice == "0":
            print("\n  Goodbye!\n")
            break
        elif choice in menu_options:
            menu_options[choice](conn)
        else:
            print("  Invalid choice. Please enter a number from the menu.")

    conn.close()


if __name__ == "__main__":
    main()