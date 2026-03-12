import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
)

cur = conn.cursor()
cur.execute("SELECT current_database(), current_user, version();")
db_name, db_user, db_version = cur.fetchone()

print("Connected successfully!")
print("Database:", db_name)
print("User:", db_user)
print("PostgreSQL version:", db_version)

cur.close()
conn.close()
