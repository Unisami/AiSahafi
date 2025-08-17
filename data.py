import sqlite3
import hashlib

# Connect to SQLite database (creates file if it doesn’t exist)
conn = sqlite3.connect("hashes.db")
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS hashes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hash TEXT NOT NULL
)
""")

conn.commit()

class HashStore:
    def __init__(self):
        self.conn = sqlite3.connect("hashes.db")
        self.cursor = self.conn.cursor()

    # Function to insert data and its hash
    def save_hash(self, data: str):
        hash_value = hashlib.sha256(str(data).encode()).hexdigest()
        self.cursor.execute("INSERT INTO hashes (hash) VALUES (?)", (hash_value,))
        self.conn.commit()
        print(f"Saved: {data} -> {hash_value}")

    # check if a specific data already exists, return True or False
    def hash_exists(self, data: str) -> bool:
        hash_value = hashlib.sha256(str(data).encode()).hexdigest()
        self.cursor.execute("SELECT 1 FROM hashes WHERE hash = ?", (hash_value,))
        return self.cursor.fetchone() is not None
    
