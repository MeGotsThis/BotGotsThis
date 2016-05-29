from ..databasebase import DatabaseBase
from bot.data.return_ import AutoJoinChannel
from contextlib import closing
import sqlite3

class SQLiteDatabase(DatabaseBase):
    __slots__ = DatabaseBase.__slots__ + (
        '_dbfile', '_oauthfile', '_timeoutlogfile')
    
    def __init__(self, ini, *args):
        super().__init__(*args)
        self._engine = 'SQLite'
        self._dbfile = ini['file']
        self._oauthfile = ini['oauth']
        self._timeoutlogfile = ini['timeoutlog']
    
    def __enter__(self):
        kwargs = {
            'database': self._dbfile,
            'detect_types': sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            }
        self._connection = sqlite3.connect(**kwargs)
        return self
    
    def getAutoJoinsChats(self):
        query = '''
SELECT broadcaster, priority, cluster FROM auto_join ORDER BY priority ASC'''
        rowMap = lambda r: AutoJoinChannel(*r)
        with closing(self.connection.cursor()) as cursor:
            yield from map(rowMap, cursor.execute(query))
    
    def getAutoJoinsPriority(self, broadcaster):
        query = '''SELECT priority FROM auto_join WHERE broadcaster=?'''
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, (broadcaster,))
            autoJoinRow = cursor.fetchone()
            if autoJoinRow is not None:
                return int(autoJoinRow[0])
            else:
                return float('inf')
            return priority
    
    def saveAutoJoin(self, broadcaster, priority=0, cluster='aws'):
        query = '''
INSERT INTO auto_join (broadcaster, priority, cluster) VALUES (?, ?, ?)'''
        with closing(self.connection.cursor()) as cursor:
            try:
                cursor.execute(query, (broadcaster, priority, cluster))
                self.connection.commit()
                return True
            except sqlite3.IntegrityError:
                return False
    
    def discardAutoJoin(self, broadcaster):
        query = '''DELETE FROM auto_join WHERE broadcaster=?'''
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, (broadcaster,))
            self.connection.commit()
            return cursor.rowcount != 0
    
    def setAutoJoinPriority(self, broadcaster, priority):
        query = '''UPDATE auto_join SET priority=? WHERE broadcaster=?'''
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, (priority, broadcaster))
            self.connection.commit()
            return cursor.rowcount != 0
    
    def setAutoJoinServer(self, broadcaster, cluster='aws'):
        query = '''UPDATE auto_join SET cluster=? WHERE broadcaster=?'''
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, (cluster, broadcaster))
            self.connection.commit()
            return cursor.rowcount != 0
    
    def getOAuthToken(self, broadcaster):
        attach = '''ATTACH DATABASE ? AS oauth'''
        query = '''SELECT token FROM oauth.oauth_tokens WHERE broadcaster=?'''
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(attach, (self._oauthfile,))
            cursor.execute(query, (broadcaster,))
            token = cursor.fetchone()
            return token and token[0]
    
    def saveBroadcasterToken(self, broadcaster, token):
        query = '''
REPLACE INTO oauth_tokens (broadcaster, token) VALUES (?, ?)'''
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, (broadcaster, token))
            self.connection.commit()
    
    def getChatCommands(self, broadcaster, command):
        query = '''
SELECT broadcaster, permission, fullMessage
    FROM custom_commands WHERE broadcaster IN (?, \'#global\') AND command=?'''
        with closing(self.connection.cursor()) as cursor:
            commands = {broadcaster: {}, '#global': {}}
            for row in cursor.execute(query, (broadcaster, command)):
                commands[row[0]][row[1]] = row[2]
            cursor.close()
            return commands
    
    def getFullGameTitle(self, abbreviation):
        query = '''
SELECT twitchGame FROM game_abbreviations WHERE abbreviation=?'''
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, (abbreviation,))
            game = cursor.fetchone()
            return game and game[0]
    
    def insertCustomCommand(self, broadcaster, permission, command,
                            fullMessage, user):
        query = '''
INSERT INTO custom_commands
    (broadcaster, permission, command, commandDisplay, fullMessage, creator,
    created, lastEditor, lastUpdated)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, CURRENT_TIMESTAMP)'''
        history = '''
INSERT INTO custom_commands_history
    (broadcaster, permission, command, commandDisplay, fullMessage, creator,
    created)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)'''
        with closing(self.connection.cursor()) as cursor:
            try:
                display = None if command.lower() == command else command
                cursor.execute(query, (broadcaster, permission,
                                       command.lower(), display, fullMessage,
                                       user, user))
            except sqlite3.IntegrityError:
                return False
            
            cursor.execute(history, (broadcaster, permission, command.lower(),
                                     history, fullMessage, user))
            self.connection.commit()
            return True
    
    def updateCustomCommand(self, broadcaster, permission, command,
                            fullMessage, user):
        query = '''
UPDATE custom_commands
    SET commandDisplay=?, fullMessage=?, lastEditor=?,
        lastUpdated=CURRENT_TIMESTAMP
    WHERE broadcaster=? AND permission=? AND command=?'''
        history = '''
INSERT INTO custom_commands_history
    (broadcaster, permission, command, commandDisplay, fullMessage, creator,
    created)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)'''
        with closing(self.connection.cursor()) as cursor:
            display = None if command.lower() == command else command
            cursor.execute(query, (display, fullMessage, user,broadcaster,
                                    permission, command.lower()))
            self.connection.commit()
            if cursor.rowcount == 0:
                return False
            
            cursor.execute(history, (broadcaster, permission, command.lower(),
                                     display, fullMessage, user))
            self.connection.commit()
            return True
    
    def replaceCustomCommand(self, broadcaster, permission, command,
                             fullMessage, user):
        query = '''
REPLACE INTO custom_commands
    (broadcaster, permission, command, commandDisplay, fullMessage, creator,
    created, lastEditor, lastUpdated)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, CURRENT_TIMESTAMP)'''
        history = '''
INSERT INTO custom_commands_history 
    (broadcaster, permission, command, commandDisplay, fullMessage, creator,
    created)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)'''
        with closing(self.connection.cursor()) as cursor:
            display = None if command.lower() == command else command
            cursor.execute(query, (broadcaster, permission, command.lower(),
                                   display, fullMessage, user, user))
            self.connection.commit()
            if cursor.rowcount == 0:
                return False
            
            cursor.execute(history, (broadcaster, permission, command.lower(),
                                     display, None, user))
            cursor.execute(history, (broadcaster, permission, command.lower(),
                                     display, fullMessage, user))
            self.connection.commit()
            return True
    
    def appendCustomCommand(self, broadcaster, permission, command,
                            message, user):
        find = '''
SELECT fullMessage FROM custom_commands
    WHERE broadcaster=? AND permission=? AND command=?'''
        query = '''
UPDATE custom_commands
    SET fullMessage=?, lastEditor=?, lastUpdated=CURRENT_TIMESTAMP
    WHERE broadcaster=? AND permission=? AND command=?'''
        history = '''
INSERT INTO custom_commands_history
    (broadcaster, permission, command, commandDisplay, fullMessage, creator,
    created)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)'''
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(find, (broadcaster, permission, command.lower()))
            original = cursor.fetchone()
            if original is None:
                return False
            fullMessage = original[0] + message
            
            display = None if command.lower() == command else command
            cursor.execute(query, (fullMessage, user, broadcaster, permission,
                                   command.lower()))
            self.connection.commit()
            if cursor.rowcount == 0:
                return False
            
            cursor.execute(history, (broadcaster, permission, command.lower(),
                                     display, fullMessage, user))
            self.connection.commit()
            return True
    
    def deleteCustomCommand(self, broadcaster, permission, command, user):
        query = '''
DELETE FROM custom_commands
    WHERE broadcaster=? AND permission=? AND command=?'''
        history = '''
INSERT INTO custom_commands_history
    (broadcaster, permission, command, commandDisplay, fullMessage, creator,
    created)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)'''
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, (broadcaster, permission, command.lower()))
            
            self.connection.commit()
            if cursor.rowcount == 0:
                return False
            
            display = None if command.lower() == command else command
            cursor.execute(history, (broadcaster, permission, command.lower(),
                                     display, None, user))
            self.connection.commit()
            return True
    
    def getCustomCommandProperty(self, broadcaster, permission, command,
                                 property=None):
        with closing(self.connection.cursor()) as cursor:
            if property is None:
                query = '''
SELECT property, value FROM custom_command_properties
    WHERE broadcaster=? AND permission=? AND command=?'''
                values = {}
                for p, v in cursor.execute(query, (broadcaster, permission,
                                                   command.lower())):
                    values[p] = v
                return values
            elif isinstance(property, list):
                query = '''
SELECT property, value FROM custom_command_properties
    WHERE broadcaster=? AND permission=? AND command=?
        AND property IN (%s)''' % ','.join('?' * len(property))
                values = {}
                params = (broadcaster, permission, command.lower(),
                          ) + tuple(property)
                for p, v in cursor.execute(query, params):
                    values[p] = v
                for p in property:
                    if p not in values:
                        values[p] = None
                return values
            else:
                query = '''
SELECT value FROM custom_command_properties 
    WHERE broadcaster=? AND permission=? AND command=? AND property=?'''
                cursor.execute(query, (broadcaster, permission,
                                       command.lower(), property))
                row = cursor.fetchone()
                return row or row[0]
    
    def processCustomCommandProperty(self, broadcaster, permission, command,
                                     property, value):
        with closing(self.connection.cursor()) as cursor:
            try:
                if value is None:
                    query = '''
DELETE FROM custom_command_properties
    WHERE broadcaster=? AND permission=? AND command=? AND property=?'''
                    cursor.execute(query, (broadcaster, permission,
                                           command.lower(), property))
                else:
                    query = '''
REPLACE INTO custom_command_properties
    (broadcaster, permission, command, property, value)
    VALUES (?, ?, ?, ?, ?)'''
                    cursor.execute(query, (broadcaster, permission,
                                           command.lower(), property, value))
                self.connection.commit()
                return cursor.rowcount != 0
            except:
                return False
    
    def hasFeature(self, broadcaster, feature):
        query = '''
SELECT 1 FROM chat_features WHERE broadcaster=? AND feature=?'''
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, (broadcaster, feature))
            return cursor.fetchone() is not None
    
    def addFeature(self, broadcaster, feature):
        query = '''
INSERT INTO chat_features (broadcaster, feature) VALUES (?, ?)'''
        with closing(self.connection.cursor()) as cursor:
            try:
                cursor.execute(query, (broadcaster, feature))
                self.connection.commit()
                return True
            except sqlite3.IntegrityError:
                return False
    
    def removeFeature(self, broadcaster, feature):
        query = '''
DELETE FROM chat_features WHERE broadcaster=? AND feature=?'''
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, (broadcaster, feature))
            self.connection.commit()
            return cursor.rowcount != 0
    
    def listBannedChannels(self):
        query = '''SELECT broadcaster FROM banned_channels'''
        with closing(self.connection.cursor()) as cursor:
            for row in cursor.execute(query):
                yield row[0]
    
    def isChannelBannedReason(self, broadcaster):
        query = '''
SELECT reason FROM banned_channels WHERE broadcaster=?'''
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, (broadcaster,))
            row = cursor.fetchone()
            return row and row[0]
    
    def addBannedChannel(self, broadcaster, reason, nick):
        query = '''
INSERT INTO banned_channels 
    (broadcaster, currentTime, reason, who)
    VALUES (?, CURRENT_TIMESTAMP, ?, ?)'''
        history = '''
INSERT INTO banned_channels_log
    (broadcaster, currentTime, reason, who, actionLog) 
    VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?)'''
        with closing(self.connection.cursor()) as cursor:
            try:
                cursor.execute(query, (broadcaster, reason, nick))
                self.connection.commit()
            except sqlite3.IntegrityError:
                return False
            
            cursor.execute(history, (broadcaster, reason, nick, 'add'))
            self.connection.commit()
            return True
    
    def removeBannedChannel(self, broadcaster, reason, nick):
        query = '''
DELETE FROM banned_channels WHERE broadcaster=?'''
        history = '''
INSERT INTO banned_channels_log
    (broadcaster, currentTime, reason, who, actionLog) 
    VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?)'''
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, (broadcaster,))
            self.connection.commit()
            if cursor.rowcount == 0:
                return False

            cursor.execute(history, (broadcaster, reason, nick, 'remove'))
            self.connection.commit()
            return True
    
    def recordTimeout(self, broadcaster, user, fromUser, module, level, length,
                      message, reason):
        attach = '''
ATTACH DATABASE ? AS timeout'''
        query = '''
INSERT INTO timeout.timeout_logs 
    (broadcaster, twitchUser, fromUser, module, level, length, message, reason)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(attach, (self._timeoutlogfile,))
            try:
                cursor.execute(query, (broadcaster, user, fromUser, module,
                                       level, length, message, reason))
                self.connection.commit()
                return True
            except sqlite3.IntegrityError:
                return False
        
    def getChatProperty(self, broadcaster, property, default=None, parse=None):
        query = '''
SELECT value FROM chat_properties WHERE broadcaster=? AND property=?'''
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, (broadcaster, property,))
            row = cursor.fetchone()
            if row is None:
                return default
            if parse is not None:
                return parse(row[0])
            return row[0]
    
    def getChatProperties(self, broadcaster, properties=[], default=None,
                          parse=None):
        query = '''
SELECT property, value FROM chat_properties
    WHERE broadcaster=? AND property IN (%s)
''' % ','.join('?' * len(properties)) + ')'
        with closing(self.connection.cursor()) as cursor:
            values = {}
            params = (broadcaster,) + tuple(properties)
            for property, value in cursor.execute(query, params):
                if isinstance(parse, dict) and property in parse:
                    value = parse[property](value)
                elif parse is not None:
                    value = parse(value)
                values[property] = value
            for property in properties:
                if property not in values:
                    if isinstance(default, dict) and property in default:
                        value = default[property]
                    else:
                        value = default
                    values[property] = value
            return values
    
    def setChatProperty(self, broadcaster, property, value=None):
        with closing(self.connection.cursor()) as cursor:
            if value is None:
                query = '''
DELETE FROM chat_properties WHERE broadcaster=? AND property=?'''
                params = broadcaster, property,
            else:
                query = '''
REPLACE INTO chat_properties (broadcaster, property, value) VALUES (?, ?, ?)'''
                params = broadcaster, property, value,
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.rowcount != 0
