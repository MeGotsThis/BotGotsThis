import database.database
import sqlite3

class SQLiteDatabase(database.database.DatabaseBase):
    __slots__ = database.database.DatabaseBase.__slots__ + ('_dbfile',)
    
    def __init__(self, ini, *args):
        super().__init__(*args)
        self._engine = 'SQLite'
        self._dbfile = ini['file']
    
    def __enter__(self):
        self._connection = sqlite3.connect(self._dbfile)
        return self
    
    def getAutoJoinsChats(self):
        cursor = self.connection.cursor()
        query = 'SELECT broadcaster FROM auto_join ORDER BY priority ASC'
        cursor.execute(query)
        chats = map(lambda r: r[0], cursor.fetchall())
        cursor.close()
        return list(chats)
    
    def getOAuthToken(self, broadcaster):
        cursor = self.connection.cursor()
        query = 'SELECT token FROM oauth_tokens WHERE broadcaster=?'
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
        query = 'SELECT broadcaster, permission, fullText '
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

