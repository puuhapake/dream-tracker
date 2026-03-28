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
