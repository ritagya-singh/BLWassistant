import sqlite3
import os

BASE_DIR = os.path.dirname(__file__)

db_path = os.path.join(BASE_DIR, "railway_pf.db")
schema_path = os.path.join(BASE_DIR, "schema.sql")

conn = sqlite3.connect(db_path)

with open(schema_path, "r") as file:
    conn.executescript(file.read())

conn.commit()
conn.close()

print("Database created successfully!")