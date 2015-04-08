CREATE TABLE auto_join (
    broadcaster VARCHAR NOT NULL PRIMARY KEY,
    priority INT NOT NULL DEFAULT 0,
    useEvent BOOL NOT NULL DEFAULT 0
);

CREATE TABLE oauth_tokens (
    broadcaster VARCHAR NOT NULL PRIMARY KEY,
    token VARCHAR NOT NULL UNIQUE ON CONFLICT REPLACE
);

CREATE TABLE custom_commands (
    broadcaster VARCHAR NOT NULL,
    permission VARCHAR NOT NULL,
    command VARCHAR NOT NULL,
    commandDisplay VARCHAR,
    fullText VARCHAR NOT NULL,
    PRIMARY KEY (broadcaster, permission, command)
);

CREATE INDEX command_broadcaster ON custom_commands (broadcaster, command);

CREATE TABLE banned_channels (
	broadcaster VARCHAR NOT NULL PRIMARY KEY,
	currentTime TIMESTAMP NOT NULL,
	reason VARCHAR NOT NULL,
	who VARCHAR NOT NULL
);

CREATE TABLE banned_channels_log (
	broadcaster VARCHAR NOT NULL,
	currentTime TIMESTAMP NOT NULL,
	reason VARCHAR NOT NULL,
	who VARCHAR NOT NULL,
	actionLog VARCHAR NOT NULL
);

CREATE TABLE chat_features (
    broadcaster VARCHAR NOT NULL,
    feature VARCHAR NOT NULL,
    PRIMARY KEY (broadcaster, feature)
);

CREATE TABLE game_abbreviations (
    abbreviation VARCHAR NOT NULL PRIMARY KEY,
    twitchGame VARCHAR NOT NULL
);
