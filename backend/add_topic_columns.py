import sqlite3

DB_PATH = "civiclens.db"

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

cursor.execute("ALTER TABLE feedback ADD COLUMN predicted_topic TEXT")
cursor.execute("ALTER TABLE feedback ADD COLUMN topic_score REAL")

connection.commit()

connection.close()

print("Topic columns added successfully!")