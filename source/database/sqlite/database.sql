CREATE TABLE auto_join (
    broadcaster VARCHAR NOT NULL PRIMARY KEY,
    priority INT NOT NULL DEFAULT 0,
    useEvent BOOL NOT NULL DEFAULT 0
);

CREATE TABLE custom_commands (
    broadcaster VARCHAR NOT NULL,
    permission VARCHAR NOT NULL,
    command VARCHAR NOT NULL,
    commandDisplay VARCHAR,
    fullMessage VARCHAR NOT NULL,
    creator VARCHAR,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    lastEditor VARCHAR,
    lastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (broadcaster, permission, command)
);

CREATE INDEX command_broadcaster ON custom_commands (broadcaster, command);

CREATE TABLE custom_command_properties (
    broadcaster VARCHAR NOT NULL,
    permission VARCHAR NOT NULL,
    command VARCHAR NOT NULL,
    property VARCHAR NOT NULL,
    value VARCHAR NOT NULL,
    PRIMARY KEY (broadcaster, permission, command, property),
    FOREIGN KEY (broadcaster, permission, command) REFERENCES custom_commands(broadcaster, permission, command)
);

CREATE TABLE custom_commands_history (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    broadcaster VARCHAR NOT NULL,
    permission VARCHAR NOT NULL,
    command VARCHAR NOT NULL,
    commandDisplay VARCHAR,
    fullMessage VARCHAR,
    creator VARCHAR,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX custom_commands_history_broadcaster ON custom_commands_history (broadcaster, command);

CREATE TABLE banned_channels (
	broadcaster VARCHAR NOT NULL PRIMARY KEY,
	currentTime TIMESTAMP NOT NULL,
	reason VARCHAR NOT NULL,
	who VARCHAR NOT NULL
);

CREATE TABLE banned_channels_log (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
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

CREATE TABLE chat_properties (
    broadcaster VARCHAR NOT NULL,
    property VARCHAR NOT NULL,
    value VARCHAR NOT NULL,
    PRIMARY KEY (broadcaster, property)
);
