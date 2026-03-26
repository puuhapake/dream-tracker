import db

def add(user_id, title, quality, dream):
    db.execute("""
        INSERT INTO Posts (poster_id, title, sleep_quality, dream)
        VALUES (?, ?, ?, ?)
    """, [user_id, title, quality, dream])

def get(uid=None):
    if uid is None:
        query = """
            SELECT p.id, p.title, u.username
            FROM Posts p, Users u
            WHERE p.poster_id = u.id
            ORDER BY p.id DESC"""
        return db.query(query)
    if isinstance(uid, int):
        query = """
            SELECT u.id uid, p.id pid, 
                   p.title, u.username,
                   p.sleep_quality, p.dream
            FROM Posts p, Users u
            WHERE p.poster_id = u.id
              AND p.id = ?"""
        return db.query(query, [uid])[0]
    else:
        raise NotImplementedError

def update(pid, title, quality, dream):
    db.execute("""UPDATE Posts
    SET title = ?,
        dream = ?,
        sleep_quality = ?
    WHERE id = ?
    """, [title, quality, dream, pid])

def user_count():
    query = "SELECT COUNT(id) count FROM Users"
    return db.query(query)[0]["count"]

def post_count():
    query = "SELECT COUNT(id) count FROM Posts"
    return db.query(query)[0]["count"]