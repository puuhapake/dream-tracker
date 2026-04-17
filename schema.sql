CREATE TABLE Users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    created_at DATETIME
);

CREATE TABLE Posts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES Users(id),
    title TEXT,
    sleep_quality INTEGER,
    dream TEXT,
    visibility TEXT,
    bedtime DATETIME,
    sleep_delay INTEGER,
    
    CHECK (
        sleep_quality BETWEEN 1 AND 5
        AND visibility IN (
            "public", "private", "friends-only"
        )
        AND sleep_delay BETWEEN 0 AND 775
    )
);

CREATE TABLE Comments (
    id INTEGER PRIMARY KEY,
    post_id INTEGER REFERENCES Posts(id),
    user_id INTEGER REFERENCES Users(id),
    content TEXT NOT NULL
);

CREATE TABLE Likes (
    id INTEGER PRIMARY KEY,
    post_id INTEGER REFERENCES Posts(id),
    user_id INTEGER REFERENCES Users(id),
    UNIQUE(post_id, user_id)
);

CREATE TABLE Friends (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES Users(id),
    friend_id INTEGER REFERENCES Users(id)
);

CREATE TABLE Tags (
    id INTEGER PRIMARY KEY,
    post_id INTEGER REFERENCES Posts(id),
    tag TEXT NOT NULL,
    UNIQUE(post_id, tag)
);

CREATE TABLE Categories (
    id INTEGER PRIMARY KEY,
    category TEXT NOT NULL,
    choice TEXT UNIQUE NOT NULL 
);

CREATE TABLE PostCategories (
    id INTEGER PRIMARY KEY,
    post_id INTEGER REFERENCES Posts(id),
    category TEXT,
    choice TEXT
);
