import db

def get_categories():
    query = "SELECT category, choice FROM Categories ORDER BY id"
    result = db.query(query)

    categories = {c["category"]: [] for c in result}
    for category, choice in result:
        categories[category].append(choice)
    
    return categories

def add(user_id, title, quality, dream, 
        visibility, bedtime, delay):
    """Adds a post to the database."""
    db.execute("""
        INSERT INTO Posts (
            user_id, title, sleep_quality, dream,
            visibility, bedtime, sleep_delay
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [
        user_id, title, quality, dream, visibility,
        bedtime, delay
    ])

def get(user_id=None):
    """Gets a post from the database. 
    Omit the 'user_id' property to retrieve all available posts.
    """
    if user_id is None:
        query = """
            SELECT p.id, p.title, p.dream dream,
                   p.visibility,
                   u.username, u.id user_id
            FROM Posts p, Users u
            WHERE p.user_id = u.id
            ORDER BY p.id DESC"""
        return db.query(query)
    if isinstance(user_id, (int, str)):
        # TODO better type safety
        query = """
            SELECT u.id user_id, p.id post_id, 
                   p.title, u.username,
                   p.sleep_quality, p.dream,
                   p.visibility
            FROM Posts p, Users u
            WHERE p.user_id = u.id
              AND p.id = ?"""
        post = db.query(query, [user_id])
        return post[0] if post else None
    raise NotImplementedError

def get_popular_posts():
    query = """
        SELECT p.id, p.title, p.dream dream,
               p.visibility,
               u.username, u.id user_id,
               COUNT(l.id) like_count
        FROM Posts p
        JOIN Users u ON p.user_id = u.id
        LEFT JOIN Likes l ON l.post_id = p.id
        GROUP BY p.id
        ORDER BY like_count DESC, p.id DESC"""
    return db.query(query)

def get_friend_posts(user_id):
    query = """
        SELECT p.id, p.title, p.dream dream,
               p.visibility,
               u.username, u.id user_id
        FROM Posts p
        JOIN Users u ON p.user_id = u.id
        JOIN Friends f ON f.friend_id = p.user_id
        WHERE f.user_id = ?
        ORDER BY p.id DESC"""
    return db.query(query, [user_id])

def update(post_id, title, quality, dream, visibility):
    """Modifies a post's content."""
    db.execute("""
    UPDATE Posts
    SET title = ?,
        dream = ?,
        sleep_quality = ?,
        visibility = ?
    WHERE id = ?
    """, [title, dream, quality, visibility, post_id])

def delete(post_id):
    """Removes a post from the database."""
    delete_tags(post_id)
    db.execute("DELETE FROM PostCategories WHERE post_id = ?", [post_id])
    db.execute("DELETE FROM Likes WHERE post_id = ?", [post_id])
    db.execute("DELETE FROM Comments WHERE post_id = ?", [post_id])
    db.execute("DELETE FROM Posts WHERE id = ?", [post_id])

# TODO better filter handling
def find(query, quality=""):
    """Finds a post whose title or content contains the given query."""
    ex = f"%{query}%"

    if quality != "":
        return db.query("""
            SELECT id, title
            FROM Posts
            WHERE sleep_quality = ?
              AND (title LIKE ? 
               OR dream LIKE ?)
            ORDER BY id DESC
        """, [quality, ex, ex])
    
    return db.query("""
        SELECT id, title
        FROM Posts
        WHERE title LIKE ?
           OR dream LIKE ?
        ORDER BY id DESC
    """, [ex, ex])

def classify(post_id):
    return db.query("""
        SELECT category, choice FROM PostCategories WHERE post_id = ?
    """, [post_id])

def update_categories(post_id, categories):
    db.execute("DELETE FROM PostCategories WHERE post_id = ?", [post_id])
    for cat, choice in categories:
        db.execute("""
            INSERT INTO PostCategories (post_id, category, choice)
            VALUES (?, ?, ?)""", [post_id, cat, choice])

def add_tags(post_id, tags):
    post_tags = []
    for t in tags:
        post_tags.append((post_id, t))

    db.executemany(
        """INSERT INTO Tags (post_id, tag)
        VALUES (?, ?)""",
        post_tags
    )

def delete_tags(post_id):
    db.execute("DELETE FROM Tags WHERE post_id = ?", [post_id])

def get_tags(post_id):
    return db.query("SELECT tag FROM Tags WHERE post_id = ?", [post_id])

def add_comment(post_id, user_id, content):
    db.execute("""
        INSERT INTO Comments (post_id, user_id, content)
        VALUES (?, ?, ?)
    """, [post_id, user_id, content])

def get_comments(post_id):
    return db.query("""
        SELECT c.content, c.id comment_id, 
               u.id user_id, u.username
        FROM Comments c, Users u
        WHERE c.post_id = ? AND c.user_id = u.id
        ORDER BY c.id DESC
    """, [post_id])

def comment_count(post_id):
    query = "SELECT COUNT(post_id) count FROM Comments WHERE post_id = ?"
    return db.query(query, [post_id])

def like(post_id, user_id, state):
    if state:
        db.execute("""
            INSERT INTO Likes (post_id, user_id)
            VALUES (?, ?)
        """, [post_id, user_id])
    else:
        db.execute("""
            DELETE FROM Likes
            WHERE post_id = ? 
            AND user_id = ?
        """, [post_id, user_id])

def get_likes(post_id):
    query = "SELECT user_id FROM Likes WHERE post_id = ?"
    return db.query(query, [post_id])

def like_count(post_id):
    query = "SELECT COUNT(user_id) count FROM Likes WHERE post_id = ?"
    return db.query(query, [post_id])[0]["count"]

def user_count():
    query = "SELECT COUNT(id) count FROM Users"
    return db.query(query)[0]["count"]

def post_count():
    query = "SELECT COUNT(id) count FROM Posts"
    return db.query(query)[0]["count"]
