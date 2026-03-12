from app.db import get_connection

conn = get_connection()
cur = conn.cursor()

cur.execute("""
INSERT INTO users (first_name, last_name, email)
VALUES ('John', 'Doe', 'john@example.com')
RETURNING user_id;
""")

user_id = cur.fetchone()[0]

conn.commit()

print("Inserted user with ID:", user_id)

cur.close()
conn.close()
