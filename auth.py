import sqlite3
import bcrypt

DB = "database.db"

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password BLOB
        )
        """)

def create_user(email, password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        with sqlite3.connect(DB) as conn:
            conn.execute(
                "INSERT INTO users (email, password) VALUES (?, ?)",
                (email, hashed)
            )
        return True
    except sqlite3.IntegrityError:
        return False

def verify_user(email, password):
    with sqlite3.connect(DB) as conn:
        cur = conn.execute(
            "SELECT password FROM users WHERE email=?",
            (email,)
        )
        row = cur.fetchone()
        if row and bcrypt.checkpw(password.encode(), row[0]):
            return True
    return False