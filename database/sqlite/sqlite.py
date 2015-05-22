import database.databasebase
import sqlite3

class SQLiteDatabase(database.databasebase.DatabaseBase):
    __slots__ = database.databasebase.DatabaseBase.__slots__ + (
        '_dbfile', '_oauthfile',)
    
    def __init__(self, ini, *args):
        super().__init__(*args)
        self._engine = 'SQLite'
        self._dbfile = ini['file']
        self._oauthfile = ini['oauth']
    
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
        except Exception:
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
        except Exception:
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
        except Exception:
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
        except Exception:
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
        except Exception:
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

            query = 'INSERT INTO custom_commands_history '
            query += '(broadcaster, permission, command, '
            query += 'commandDisplay, fullMessage, creator, created) '
            query += 'VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)'
            display = None if command.lower() == command else command
            params = broadcaster, permission, command.lower(),
            params += display, fullMessage, user
            cursor.execute(query, params)

            self.connection.commit()
            if cursor.rowcount == 0:
                return False
            return True
        except Exception:
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
        except Exception:
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
        except Exception:
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
        except Exception:
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
        except Exception:
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
        except Exception:
            return False
        finally:
            cursor.close()
    
    def listBannedChannels(self):
        cursor = self.connection.cursor()
        try:
            query = 'SELECT broadcaster FROM banned_channels'
            cursor.execute(query)
            return [r[0] for r in cursor.fetchall()]
        except Exception as e:
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
        except Exception:
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
        except Exception:
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
        except Exception:
            return False
        finally:
            cursor.close()
