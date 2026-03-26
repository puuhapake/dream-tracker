CREATE TABLE Users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE Posts (
    id INTEGER PRIMARY KEY,
    poster_id INTEGER REFERENCES Users(id),
    title TEXT,
    sleep_quality TEXT,
    dream TEXT
);