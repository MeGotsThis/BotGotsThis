CREATE TABLE timeout_logs (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    theTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    broadcaster VARCHAR NOT NULL,
    twitchUser VARCHAR NOT NULL,
    fromUser VARCHAR,
    module VARCHAR NOT NULL,
    level INTEGER,
    length INTEGER,
    message VARCHAR NULL,
    reason VARCHAR
);
