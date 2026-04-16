from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from datetime import datetime

import db

def get(user_id):
    """Retrieves the information associated with a user by uid."""
    query = """
        SELECT id, username, created_at
        FROM Users
        WHERE id = ?"""
    user = db.query(query, [user_id])
    return user[0] if user else None

def get_id(username):
    """Retrieves the user id associated with a user by username."""
    query = "SELECT id FROM Users WHERE username = ?"
    user = db.query(query, [username])
    return user[0]["id"] if user else None

def join_date(user_id, time=""):
    """Gets or formats a given user's join date."""
    if not time:
        query = "SELECT created_at FROM Users WHERE id = ?"
        time = db.query(query, [user_id])[0]["created_at"]
    time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
    return time.strftime("%d/%m/%Y")

def posts(user_id):
    """Retrieves all posts published by a user with the given uid."""
    query = """
        SELECT id, title, dream
        FROM Posts
        WHERE user_id = ?
        ORDER BY id DESC"""
    return db.query(query, [user_id])

def get_comments(user_id):
    """Retrieves all comments published by the given user ID."""
    query = """
        SELECT p.id post_id, p.title post_title, 
               c.content, c.id comment_id
        FROM Comments c
        JOIN Posts p ON c.post_id = p.id
        JOIN Users u ON c.user_id = u.id
        WHERE c.user_id = ?
        ORDER BY c.id DESC"""
    return db.query(query, [user_id])

def get_likes(user_id):
    """Retrieves all posts liked by the given user ID."""
    query = """
        SELECT p.id post_id, p.title, p.dream, 
            u.username username, u.id user_id
        FROM Likes l 
        JOIN Posts p ON l.post_id = p.id
        JOIN Users u ON u.id = p.user_id
        WHERE l.user_id = ?
        ORDER BY l.id DESC"""
    return db.query(query, [user_id])

def has_liked(user_id, post_id):
    return db.query("""
        SELECT COUNT(id) likes
        FROM Likes
        WHERE user_id = ?
          AND post_id = ?
        LIMIT 1
    """, [user_id, post_id])[0]["likes"] > 0

def is_following(follower, target_user):
    return db.query("""
        SELECT COUNT(id) follows
        FROM Friends
        WHERE user_id = ?
          AND friend_id = ?
    """, [follower, target_user])[0]["follows"] > 0

def get_followers(user_id):
    query = """
        SELECT u.id, u.username
        FROM Friends f
        JOIN Users u ON u.id = f.user_id
        WHERE f.friend_id = ?"""
    return db.query(query, [user_id])

def follow(user_id, friend_id):
    db.execute("""
        INSERT INTO Friends (user_id, friend_id)
        VALUES (?, ?)
    """, [user_id, friend_id])

def unfollow(user_id, friend_id):
    db.execute("""
        DELETE FROM Friends
        WHERE user_id = ?
          AND friend_id = ?
    """, [user_id, friend_id])

def register(username, password):
    """Creates a new user account with given username and password."""
    password_hash = generate_password_hash(password)
    sql = """INSERT INTO Users (username, password_hash, created_at)
             VALUES (?, ?, ?)"""
    db.execute(sql, [username, password_hash, datetime.now()])

    user_id = """SELECT id FROM Users WHERE username = ?"""
    return db.query(user_id, [username])[0]["id"]

# TODO Rename & rework, e.g. get_password_hash()
def login(username, password):
    """Retrieves the password hash for a user by username."""
    query = "SELECT id, password_hash FROM Users WHERE username = ?"
    sql = db.query(query, [username])
    return sql[0] if sql else None

def authenticate(password_hash, password):
    """Checks the plaintext password against the given password hash."""
    return check_password_hash(password_hash, password)
