from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from datetime import datetime

import db

def get(uid):
    """Retrieves the information associated with a user by uid."""
    query = """
        SELECT id, username, created_at
        FROM Users
        WHERE id = ?"""
    user = db.query(query, [uid])
    return user[0] if user else None

def join_date(uid, time=""):
    """Gets or formats a given user's join date."""
    if not time:
        query = "SELECT created_at FROM Users WHERE id = ?"
        time = db.query(query, [uid])[0]["created_at"]
    time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
    return time.strftime("%d/%m/%Y")

def posts(uid):
    """Retrieves all posts published by a user with the given uid."""
    query = """
        SELECT id, title
        FROM Posts
        WHERE poster_id = ?
        ORDER BY id DESC"""
    return db.query(query, [uid])

def register(username, password):
    """Creates a new user account with given username and password."""
    password_hash = generate_password_hash(password)
    sql = """INSERT INTO Users (username, password_hash, created_at)
             VALUES (?, ?, ?)"""
    db.execute(sql, [username, password_hash, datetime.now()])

    uid = """SELECT id FROM Users WHERE username = ?"""
    return db.query(uid, [username])[0]["id"]

# TODO Rename & rework, e.g. get_password_hash()
def login(username, password):
    """Retrieves the password hash for a user by username."""
    query = "SELECT id, password_hash FROM Users WHERE username = ?"
    sql = db.query(query, [username])
    return sql[0] if sql else None

def authenticate(password_hash, password):
    """Checks the plaintext password against the given password hash."""
    return check_password_hash(password_hash, password)
