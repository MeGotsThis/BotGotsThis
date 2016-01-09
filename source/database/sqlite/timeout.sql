CREATE TABLE timeout_logs (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    broadcaster VARCHAR NOT NULL,
    twitchUser VARCHAR NOT NULL,
    fromUser VARCHAR,
    module VARCHAR NOT NULL,
    level INTEGER,
    length INTEGER NOT NULL,
    message VARCHAR NULL,
    reason VARCHAR
);
