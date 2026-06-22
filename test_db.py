import sqlite3

conn = sqlite3.connect("database/railway_pf.db")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM employees")
print(cursor.fetchone())

conn.close()