from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

import db

def get(uid):
    query = """
        SELECT id, username
        FROM Users
        WHERE id = ?"""
    user = db.query(query, [uid])
    return user[0] if user else None

def posts(uid):
    query = """
        SELECT id, title
        FROM Posts
        WHERE poster_id = ?
        ORDER BY id DESC"""
    return db.query(query, [uid])

def register(username, password):
    password_hash = generate_password_hash(password)
    sql = """INSERT INTO Users (username, password_hash)
             VALUES (?, ?)"""
    db.execute(sql, [username, password_hash])

    uid = """SELECT id FROM Users WHERE username = ?"""
    return db.query(uid, [username])[0]["id"]

def login(username, password):
    query = "SELECT id, password_hash FROM Users WHERE username = ?"
    sql = db.query(query, [username])
    return sql[0] if sql else None

def authenticate(password_hash, password):
    return check_password_hash(password_hash, password)