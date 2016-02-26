from ..databasebase import DatabaseBase
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
        cursor = self.connection.cursor()
        query = 'SELECT broadcaster, priority, useEvent FROM auto_join '
        query += 'ORDER BY priority ASC'
        cursor.execute(query)
        rowMap = lambda r: {
            'broadcaster': r[0],
            'priority': r[1],
            'eventServer': r[2],
            }
        chats = map(rowMap, cursor.fetchall())
        cursor.close()
        return list(chats)
    
    def getAutoJoinsPriority(self, broadcaster):
        cursor = self.connection.cursor()
        query = 'SELECT priority FROM auto_join WHERE broadcaster=?'
        cursor.execute(query, (broadcaster,))
        autoJoinRow = cursor.fetchone()
        if autoJoinRow is not None:
            priority = int(autoJoinRow[0])
        else:
            priority = float('inf')
        cursor.close()
        return priority
    
    def saveAutoJoin(self, broadcaster, priority=0, useEvent=False):
        cursor = self.connection.cursor()
        try:
            query = 'INSERT INTO auto_join (broadcaster, priority, useEvent) '
            query += 'VALUES (?, ?, ?)'
            params = broadcaster, priority, useEvent
            cursor.execute(query, params)
            self.connection.commit()
            return True
        except:
            return False
        finally:
            cursor.close()
    
    def discardAutoJoin(self, broadcaster):
        cursor = self.connection.cursor()
        try:
            query = 'DELETE FROM auto_join WHERE broadcaster=?'
            params = broadcaster,
            cursor.execute(query, params)
            self.connection.commit()
            if cursor.rowcount == 0:
                return False
            return True
        except:
            return False
        finally:
            cursor.close()
    
    def setAutoJoinPriority(self, broadcaster, priority):
        cursor = self.connection.cursor()
        try:
            query = 'UPDATE auto_join SET priority=? WHERE broadcaster=?'
            params = priority, broadcaster
            cursor.execute(query, params)
            self.connection.commit()
            if cursor.rowcount == 0:
                return False
            return True
        except:
            return False
        finally:
            cursor.close()
    
    def setAutoJoinServer(self, broadcaster, useEvent=False):
        cursor = self.connection.cursor()
        try:
            query = 'UPDATE auto_join SET useEvent=? WHERE broadcaster=?'
            params = useEvent, broadcaster
            cursor.execute(query, params)
            self.connection.commit()
            if cursor.rowcount == 0:
                return False
            return True
        except:
            return False
        finally:
            cursor.close()
    
    def getOAuthToken(self, broadcaster):
        cursor = self.connection.cursor()
        query = 'ATTACH DATABASE ? AS oauth'
        cursor.execute(query, (self._oauthfile,))
        query = 'SELECT token FROM oauth.oauth_tokens WHERE broadcaster=?'
        cursor.execute(query, (broadcaster,))
        tokenRow = cursor.fetchone()
        token = tokenRow[0] if tokenRow is not None else None
        cursor.close()
        return token
    
    def saveBroadcasterToken(self, broadcaster, token):
        cursor = self.connection.cursor()
        query = 'REPLACE INTO oauth_tokens (broadcaster, token) VALUES (?, ?)'
        cursor.execute(query, (broadcaster, token))
        self.connection.commit()
        cursor.close()
    
    def getChatCommands(self, broadcaster, command):
        cursor = self.connection.cursor()
        query = 'SELECT broadcaster, permission, fullMessage '
        query += 'FROM custom_commands '
        query += 'WHERE broadcaster IN (?, \'#global\') AND command=?'
        commands = {broadcaster: {}, '#global': {}}
        for row in cursor.execute(query, (broadcaster, command)):
            commands[row[0]][row[1]] = row[2]
        cursor.close()
        return commands
    
    def getFullGameTitle(self, abbreviation):
        cursor = self.connection.cursor()
        query = 'SELECT twitchGame FROM game_abbreviations '
        query += 'WHERE abbreviation=?'
        cursor.execute(query, (abbreviation,))
        gameRow = cursor.fetchone()
        game = gameRow[0] if gameRow is not None else None
        cursor.close()
        return game
    
    def insertCustomCommand(self, broadcaster, permission, command,
                            fullMessage, user):
        cursor = self.connection.cursor()
        try:
            query = 'INSERT INTO custom_commands '
            query += '(broadcaster, permission, command, '
            query += 'commandDisplay, fullMessage, creator, created, '
            query += 'lastEditor, lastUpdated) '
            query += 'VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, '
            query += 'CURRENT_TIMESTAMP)'
            display = None if command.lower() == command else command
            params = broadcaster, permission, command.lower(),
            params += display, fullMessage, user, user
            cursor.execute(query, params)

            query = 'INSERT INTO custom_commands_history '
            query += '(broadcaster, permission, command, '
            query += 'commandDisplay, fullMessage, creator, created) '
            query += 'VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)'
            display = None if command.lower() == command else command
            params = broadcaster, permission, command.lower(),
            params += display, fullMessage, user
            cursor.execute(query, params)

            self.connection.commit()
            return True
        except:
            return False
        finally:
            cursor.close()
    
    def updateCustomCommand(self, broadcaster, permission, command,
                            fullMessage, user):
        cursor = self.connection.cursor()
        try:
            query = 'UPDATE custom_commands SET commandDisplay=?, '
            query += 'fullMessage=?, lastEditor=?, '
            query += 'lastUpdated=CURRENT_TIMESTAMP '
            query += 'WHERE broadcaster=? AND permission=? AND command=?'
            display = None if command.lower() == command else command
            params = display, fullMessage, user,
            params += broadcaster, permission, command.lower()
            cursor.execute(query, params)

            self.connection.commit()
            if cursor.rowcount == 0:
                return False

            query = 'INSERT INTO custom_commands_history '
            query += '(broadcaster, permission, command, '
            query += 'commandDisplay, fullMessage, creator, created) '
            query += 'VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)'
            display = None if command.lower() == command else command
            params = broadcaster, permission, command.lower(),
            params += display, fullMessage, user
            cursor.execute(query, params)

            self.connection.commit()
            return True
        except:
            return False
        finally:
            cursor.close()
    
    def replaceCustomCommand(self, broadcaster, permission, command,
                             fullMessage, user):
        cursor = self.connection.cursor()
        try:
            query = 'REPLACE INTO custom_commands '
            query += '(broadcaster, permission, command, '
            query += 'commandDisplay, fullMessage, creator, created, '
            query += 'lastEditor, lastUpdated) '
            query += 'VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, '
            query += 'CURRENT_TIMESTAMP)'
            display = None if command.lower() == command else command
            params = broadcaster, permission, command.lower(),
            params += display, fullMessage, user, user
            cursor.execute(query, params)

            self.connection.commit()
            if cursor.rowcount == 0:
                return False

            query = 'INSERT INTO custom_commands_history '
            query += '(broadcaster, permission, command, '
            query += 'commandDisplay, fullMessage, creator, created) '
            query += 'VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)'
            display = None if command.lower() == command else command
            params = broadcaster, permission, command.lower(),
            params += display, None, user
            cursor.execute(query, params)

            query = 'INSERT INTO custom_commands_history '
            query += '(broadcaster, permission, command, '
            query += 'commandDisplay, fullMessage, creator, created) '
            query += 'VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)'
            display = None if command.lower() == command else command
            params = broadcaster, permission, command.lower(),
            params += display, fullMessage, user
            cursor.execute(query, params)

            self.connection.commit()
            return True
        except:
            return False
        finally:
            cursor.close()
    
    def appendCustomCommand(self, broadcaster, permission, command,
                            message, user):
        cursor = self.connection.cursor()
        try:
            query = 'SELECT fullMessage FROM custom_commands '
            query += 'WHERE broadcaster=? AND permission=? AND command=?'
            cursor.execute(query, (broadcaster, permission, command.lower()))
            messageRow = cursor.fetchone()
            if messageRow is None:
                return False
            fullMessage = messageRow[0] + message

            query = 'UPDATE custom_commands SET fullMessage=?, lastEditor=?, '
            query += 'lastUpdated=CURRENT_TIMESTAMP '
            query += 'WHERE broadcaster=? AND permission=? AND command=?'
            display = None if command.lower() == command else command
            params = fullMessage, user,
            params += broadcaster, permission, command.lower()
            cursor.execute(query, params)

            self.connection.commit()
            if cursor.rowcount == 0:
                return False

            query = 'INSERT INTO custom_commands_history '
            query += '(broadcaster, permission, command, '
            query += 'commandDisplay, fullMessage, creator, created) '
            query += 'VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)'
            display = None if command.lower() == command else command
            params = broadcaster, permission, command.lower(),
            params += display, fullMessage, user
            cursor.execute(query, params)

            self.connection.commit()
            return True
        except:
            return False
        finally:
            cursor.close()
    
    def deleteCustomCommand(self, broadcaster, permission, command, user):
        cursor = self.connection.cursor()
        try:
            query = 'DELETE FROM custom_commands WHERE '
            query += 'broadcaster=? AND permission=? AND command=?'
            params = broadcaster, permission, command.lower()
            cursor.execute(query, params)

            self.connection.commit()
            if cursor.rowcount == 0:
                return False

            query = 'INSERT INTO custom_commands_history '
            query += '(broadcaster, permission, command, '
            query += 'commandDisplay, fullMessage, creator, created) '
            query += 'VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)'
            display = None if command.lower() == command else command
            params = broadcaster, permission, command.lower(),
            params += display, None, user
            cursor.execute(query, params)

            self.connection.commit()
            if cursor.rowcount == 0:
                return False
            return True
        except:
            return False
        finally:
            cursor.close()
    
    def getCustomCommandProperty(self, broadcaster, permission, command,
                                 property=None):
        cursor = self.connection.cursor()
        if property is None:
            values = {}
            query = 'SELECT property, value FROM custom_command_properties '
            query += 'WHERE broadcaster=? AND permission=? AND command=?'
            params = broadcaster, permission, command,
            for p, v in cursor.execute(query, params):
                values[p] = v
            return values
        elif isinstance(property, list):
            values = {}
            query = 'SELECT property, value FROM custom_command_properties '
            query += 'WHERE broadcaster=? AND permission=? AND command=? AND '
            query += 'property IN (' + ','.join('?' * len(properties)) + ')'
            params = (broadcaster, permission, command,) + tuple(property)
            for p, v in cursor.execute(query, params):
                values[p] = v
            for p in property:
                if p not in values:
                    values[p] = None
            return values
        else:
            query = 'SELECT value FROM custom_command_properties WHERE '
            query += 'broadcaster=? AND permission=? AND command=? AND '
            query += 'property=?'
            params = broadcaster, permission, command, property
            cursor.execute(query, params)
            return (cursor.fetchone() or [None])[0]
    
    def processCustomCommandProperty(self, broadcaster, permission, command,
                                     property, value):
        cursor = self.connection.cursor()
        try:
            if value is None:
                query = 'DELETE FROM custom_command_properties WHERE '
                query += 'broadcaster=? AND permission=? AND command=? AND '
                query += 'property=?'
                params = broadcaster, permission, command, property
                cursor.execute(query, params)
            else:
                query = 'REPLACE INTO custom_command_properties '
                query += '(broadcaster, permission, command, property, value) '
                query += 'VALUES (?, ?, ?, ?, ?)'
                params = broadcaster, permission, command, property, value
                cursor.execute(query, params)

            self.connection.commit()
            if cursor.rowcount == 0:
                return False
            return True
        except:
            return False
        finally:
            cursor.close()
    
    def hasFeature(self, broadcaster, feature):
        cursor = self.connection.cursor()
        try:
            query = 'SELECT 1 FROM chat_features '
            query += 'WHERE broadcaster=? AND feature=?'
            params = broadcaster, feature
            cursor.execute(query, params)
            return cursor.fetchone() is not None
        except:
            return False
        finally:
            cursor.close()
    
    def addFeature(self, broadcaster, feature):
        cursor = self.connection.cursor()
        try:
            query = 'INSERT INTO chat_features (broadcaster, feature) '
            query += 'VALUES (?, ?)'
            params = broadcaster, feature
            cursor.execute(query, params)
            self.connection.commit()
            return True
        except:
            return False
        finally:
            cursor.close()
    
    def removeFeature(self, broadcaster, feature):
        cursor = self.connection.cursor()
        try:
            query = 'DELETE FROM chat_features '
            query += 'WHERE broadcaster=? AND feature=?'
            params = broadcaster, feature
            cursor.execute(query, params)
            self.connection.commit()
            if cursor.rowcount == 0:
                return False
            return True
        except:
            return False
        finally:
            cursor.close()
    
    def listBannedChannels(self):
        cursor = self.connection.cursor()
        try:
            query = 'SELECT broadcaster FROM banned_channels'
            cursor.execute(query)
            return [r[0] for r in cursor.fetchall()]
        except:
            return []
        finally:
            cursor.close()
    
    def isChannelBannedReason(self, broadcaster):
        cursor = self.connection.cursor()
        try:
            query = 'SELECT reason FROM banned_channels WHERE broadcaster=?'
            params = broadcaster,
            cursor.execute(query, params)
            row = cursor.fetchone()
            if row is not None:
                return row[0]
            return False
        except:
            return False
        finally:
            cursor.close()
    
    def addBannedChannel(self, broadcaster, reason, nick):
        cursor = self.connection.cursor()
        try:
            query = 'INSERT INTO banned_channels '
            query += '(broadcaster, currentTime, reason, who) '
            query += 'VALUES (?, CURRENT_TIMESTAMP, ?, ?)'
            params = broadcaster, reason, nick
            cursor.execute(query, params)

            self.connection.commit()
            if cursor.rowcount == 0:
                return False

            query = 'INSERT INTO banned_channels_log '
            query += '(broadcaster, currentTime, reason, who, actionLog) '
            query += 'VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?)'
            params = broadcaster, reason, nick, 'add'
            cursor.execute(query, params)

            self.connection.commit()
            return True
        except:
            return False
        finally:
            cursor.close()
    
    def removeBannedChannel(self, broadcaster, reason, nick):
        cursor = self.connection.cursor()
        try:
            query = 'DELETE FROM banned_channels FROM broadcaster=?'
            params = broadcaster,
            cursor.execute(query, params)

            self.connection.commit()
            if cursor.rowcount == 0:
                return False

            query = 'INSERT INTO banned_channels_log '
            query += '(broadcaster, currentTime, reason, who, actionLog) '
            query += 'VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?)'
            params = broadcaster, reason, nick, 'remove'
            cursor.execute(query, params)

            self.connection.commit()
            return True
        except:
            return False
        finally:
            cursor.close()
    
    def recordTimeout(self, broadcaster, user, fromUser, module, level, length,
                      message, reason):
        cursor = self.connection.cursor()
        try:
            query = 'ATTACH DATABASE ? AS timeout'
            cursor.execute(query, (self._timeoutlogfile,))
            query = 'INSERT INTO timeout.timeout_logs '
            query += '(broadcaster, twitchUser, fromUser, module, level, '
            query += 'length, message, reason) '
            query += 'VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
            cursor.execute(query, (broadcaster, user, fromUser, module, level,
                                   length, message, reason))

            self.connection.commit()
            if cursor.rowcount == 0:
                return False
            return True
        except:
            return False
        finally:
            cursor.close()
        
    def getChatProperty(self, broadcaster, property, default=None, parse=None):
        cursor = self.connection.cursor()
        query = 'SELECT value FROM chat_properties '
        query += 'WHERE broadcaster=? AND property=?'
        cursor.execute(query, (broadcaster, property,))
        row = cursor.fetchone()
        cursor.close()
        if row is None:
            return default
        if parse is not None:
            return parse(row[0])
        return row[0]
    
    def getChatProperties(self, broadcaster, properties=[], default=None,
                          parse=None):
        cursor = self.connection.cursor()
        query = 'SELECT property, value FROM chat_properties '
        query += 'WHERE broadcaster=? AND property IN ('
        query += ','.join('?' * len(properties)) + ')'
        params = (broadcaster,) + tuple(properties)
        values = {}
        for property, value in cursor.execute(query, params):
            if isinstance(parse, dict) and property in parse:
                value = parse[property](value)
            elif parse is not None:
                value = parse(value)
            values[property] = value
        cursor.close()
        for property in properties:
            if property not in values:
                if isinstance(default, dict) and property in default:
                    value = default[property]
                else:
                    value = default
                values[property] = value
        return values
    
    def setChatProperty(self, broadcaster, property, value=None):
        cursor = self.connection.cursor()
        try:
            if value is None:
                query = 'DELETE FROM chat_properties '
                query += 'WHERE broadcaster=? AND property=?'
                params = broadcaster, property,
            else:
                query = 'REPLACE INTO chat_properties '
                query += '(broadcaster, property, value) VALUES (?, ?, ?)'
                params = broadcaster, property, value,
            cursor.execute(query, params)

            self.connection.commit()
            if cursor.rowcount == 0:
                return False
            return True
        finally:
            cursor.close()
