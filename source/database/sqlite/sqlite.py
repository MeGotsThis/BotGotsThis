from .. import AutoJoinChannel, CommandProperty, CommandReturn, DatabaseBase
from contextlib import closing
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Sequence
from typing import Tuple, Union
import sqlite3

CommandTuple = Tuple[str, str, str]

class SQLiteDatabase(DatabaseBase):
    def __init__(self,
                 ini: Mapping[str, str],
                 **kwargs) -> None:
        super().__init__(**kwargs)
        self._engine = 'SQLite'  # type: str
        self._dbfile = ini['file']  # type: str
        self._oauthfile = ini['oauth']  # type: str
        self._timeoutlogfile = ini['timeoutlog']  # type: str
    
    def __enter__(self):
        kwargs = {
            'database': self._dbfile,
            'detect_types': sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            }
        self._connection = sqlite3.connect(**kwargs)  # type: sqlite3.Connection
        return self
    
    def getAutoJoinsChats(self) -> Iterable[AutoJoinChannel]:
        query = '''
SELECT broadcaster, priority, cluster FROM auto_join ORDER BY priority ASC'''  # type: str
        with closing(self.connection.cursor()) as cursor:  # --type: sqlite3.Cursor
            yield from map(lambda r: AutoJoinChannel(*r), cursor.execute(query))
    
    def getAutoJoinsPriority(self, broadcaster: str) -> Union[int, float]:
        query = '''SELECT priority FROM auto_join WHERE broadcaster=?'''  # type: str
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, (broadcaster,))
            autoJoinRow = cursor.fetchone()  # type: Optional[Tuple[int]]
            if autoJoinRow is not None:
                return int(autoJoinRow[0])
            else:
                return float('inf')

    def saveAutoJoin(self,
                     broadcaster: str,
                     priority: Union[int, float]=0,
                     cluster: str='aws') -> bool:
        query = '''
INSERT INTO auto_join (broadcaster, priority, cluster) VALUES (?, ?, ?)'''  # type: str
        with closing(self.connection.cursor()) as cursor:  # --type: sqlite3.Cursor
            try:
                cursor.execute(query, (broadcaster, priority, cluster))
                self.connection.commit()
                return True
            except sqlite3.IntegrityError:
                return False
    
    def discardAutoJoin(self, broadcaster: str) -> bool:
        query = '''DELETE FROM auto_join WHERE broadcaster=?'''  # type: str
        with closing(self.connection.cursor()) as cursor:  # --type: sqlite3.Cursor
            cursor.execute(query, (broadcaster,))
            self.connection.commit()
            return cursor.rowcount != 0

    def setAutoJoinPriority(self,
                            broadcaster: str,
                            priority: Union[int, float]) -> bool:
        query = '''UPDATE auto_join SET priority=? WHERE broadcaster=?'''  # type: str
        with closing(self.connection.cursor()) as cursor:  # --type: sqlite3.Cursor
            cursor.execute(query, (priority, broadcaster))
            self.connection.commit()
            return cursor.rowcount != 0

    def setAutoJoinServer(self,
                          broadcaster: str,
                          cluster: str = 'aws') -> bool:
        query = '''UPDATE auto_join SET cluster=? WHERE broadcaster=?'''  # type: str
        with closing(self.connection.cursor()) as cursor:  # --type: sqlite3.Cursor
            cursor.execute(query, (cluster, broadcaster))
            self.connection.commit()
            return cursor.rowcount != 0
    
    def getOAuthToken(self, broadcaster:str) -> Optional[str]:
        attach = '''ATTACH DATABASE ? AS oauth'''
        query = '''SELECT token FROM oauth.oauth_tokens WHERE broadcaster=?'''  # type: str
        with closing(self.connection.cursor()) as cursor:  # --type: sqlite3.Cursor
            cursor.execute(attach, (self._oauthfile,))
            cursor.execute(query, (broadcaster,))
            token = cursor.fetchone()  # type: Optional[Tuple[str]]
            return token and token[0]  # type: ignore

    def saveBroadcasterToken(self,
                             broadcaster: str,
                             token: str) -> None:
        query = '''
REPLACE INTO oauth_tokens (broadcaster, token) VALUES (?, ?)'''  # type: str
        with closing(self.connection.cursor()) as cursor:  # --type: sqlite3.Cursor
            cursor.execute(query, (broadcaster, token))
            self.connection.commit()

    def getChatCommands(self,
                        broadcaster: str,
                        command: str) -> Dict[str, Dict[str, str]]:
        query = '''
SELECT broadcaster, permission, fullMessage
    FROM custom_commands WHERE broadcaster IN (?, \'#global\') AND command=?'''  # type: str
        with closing(self.connection.cursor()) as cursor:  # --type: sqlite3.Cursor
            commands = {broadcaster: {}, '#global': {}}  # type: Dict[str, Dict[str, str]]
            for row in cursor.execute(
                    query, (broadcaster, command)):  # --type: Optional[CommandTuple]
                commands[row[0]][row[1]] = row[2]
            cursor.close()
            return commands
    
    def getFullGameTitle(self, abbreviation: str) -> Optional[str]:
        query = '''
SELECT twitchGame FROM game_abbreviations WHERE abbreviation=?'''  # type: str
        with closing(self.connection.cursor()) as cursor:  # --type: sqlite3.Cursor
            cursor.execute(query, (abbreviation,))
            game = cursor.fetchone()  # type: Optional[Tuple[str]]
            return game and game[0]  # type: ignore

    def insertCustomCommand(self,
                            broadcaster: str,
                            permission: str,
                            command: str,
                            fullMessage: str,
                            user: str) -> bool:
        query = '''
INSERT INTO custom_commands
    (broadcaster, permission, command, commandDisplay, fullMessage, creator,
    created, lastEditor, lastUpdated)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, CURRENT_TIMESTAMP)'''  # type: str
        history = '''
INSERT INTO custom_commands_history
    (broadcaster, permission, command, commandDisplay, fullMessage, creator,
    created)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)'''  # type: str
        with closing(self.connection.cursor()) as cursor:  # --type: sqlite3.Cursor
            try:
                display = None if command.lower() == command else command  # type: Optional[str]
                cursor.execute(query, (broadcaster, permission,
                                       command.lower(), display, fullMessage,
                                       user, user))
            except sqlite3.IntegrityError:
                return False
            
            cursor.execute(history, (broadcaster, permission, command.lower(),
                                     history, fullMessage, user))
            self.connection.commit()
            return True

    def updateCustomCommand(self,
                            broadcaster: str,
                            permission: str,
                            command: str,
                            fullMessage: str,
                            user: str) -> bool:
        query = '''
UPDATE custom_commands
    SET commandDisplay=?, fullMessage=?, lastEditor=?,
        lastUpdated=CURRENT_TIMESTAMP
    WHERE broadcaster=? AND permission=? AND command=?'''  # type: str
        history = '''
INSERT INTO custom_commands_history
    (broadcaster, permission, command, commandDisplay, fullMessage, creator,
    created)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)'''  # type: str
        with closing(self.connection.cursor()) as cursor:  # --type: sqlite3.Cursor
            display = None if command.lower() == command else command  # type: Optional[str]
            cursor.execute(query, (display, fullMessage, user, broadcaster,
                                   permission, command.lower()))
            self.connection.commit()
            if cursor.rowcount == 0:
                return False
            
            cursor.execute(history, (broadcaster, permission, command.lower(),
                                     display, fullMessage, user))
            self.connection.commit()
            return True

    def replaceCustomCommand(self,
                             broadcaster: str,
                             permission: str,
                             command: str,
                             fullMessage: str,
                             user: str):
        query = '''
REPLACE INTO custom_commands
    (broadcaster, permission, command, commandDisplay, fullMessage, creator,
    created, lastEditor, lastUpdated)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, CURRENT_TIMESTAMP)'''  # type: str
        history = '''
INSERT INTO custom_commands_history 
    (broadcaster, permission, command, commandDisplay, fullMessage, creator,
    created)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)'''  # type: str
        with closing(self.connection.cursor()) as cursor:  # --type: sqlite3.Cursor
            display = None if command.lower() == command else command  # type: Optional[str]
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

    def appendCustomCommand(self,
                            broadcaster: str,
                            permission: str,
                            command: str,
                            message: str,
                            user: str):
        find = '''
SELECT fullMessage FROM custom_commands
    WHERE broadcaster=? AND permission=? AND command=?'''  # type: str
        query = '''
UPDATE custom_commands
    SET fullMessage=?, lastEditor=?, lastUpdated=CURRENT_TIMESTAMP
    WHERE broadcaster=? AND permission=? AND command=?'''  # type: str
        history = '''
INSERT INTO custom_commands_history
    (broadcaster, permission, command, commandDisplay, fullMessage, creator,
    created)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)'''  # type: str
        with closing(self.connection.cursor()) as cursor:  # --type: sqlite3.Cursor
            cursor.execute(find, (broadcaster, permission, command.lower()))
            original = cursor.fetchone()  # type: Optional[Tuple[str]]
            if original is None:
                return False
            fullMessage = original[0] + message  # type: str
            
            display = None if command.lower() == command else command  # type: Optional[str]
            cursor.execute(query, (fullMessage, user, broadcaster, permission,
                                   command.lower()))
            self.connection.commit()
            if cursor.rowcount == 0:
                return False
            
            cursor.execute(history, (broadcaster, permission, command.lower(),
                                     display, fullMessage, user))
            self.connection.commit()
            return True

    def deleteCustomCommand(self,
                            broadcaster: str,
                            permission: str,
                            command: str,
                            user: str):
        query = '''
DELETE FROM custom_commands
    WHERE broadcaster=? AND permission=? AND command=?'''  # type: str
        history = '''
INSERT INTO custom_commands_history
    (broadcaster, permission, command, commandDisplay, fullMessage, creator,
    created)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)'''  # type: str
        with closing(self.connection.cursor()) as cursor:  # --type: sqlite3.Cursor
            cursor.execute(query, (broadcaster, permission, command.lower()))
            
            self.connection.commit()
            if cursor.rowcount == 0:
                return False
            
            display = None if command.lower() == command else command  # type: Optional[str]
            cursor.execute(history, (broadcaster, permission, command.lower(),
                                     display, None, user))
            self.connection.commit()
            return True

    def getCustomCommandProperty(
            self,
            broadcaster: str,
            permission: str,
            command: str,
            property: Optional[CommandProperty]=None) -> Optional[CommandReturn]:
        with closing(self.connection.cursor()) as cursor:  # --type: sqlite3.Cursor
            if property is None:
                query = '''
SELECT property, value FROM custom_command_properties
    WHERE broadcaster=? AND permission=? AND command=?'''  # type: str
                values = {}  # type: Dict[str, str]
                for p, v in cursor.execute(query, (broadcaster, permission,
                                                   command.lower())):  # --type: str, str
                    values[p] = v
                return values
            elif isinstance(property, list):
                query = '''
SELECT property, value FROM custom_command_properties
    WHERE broadcaster=? AND permission=? AND command=?
        AND property IN (%s)''' % ','.join('?' * len(property))
                values = {}
                params = (broadcaster, permission, command.lower(),
                          ) + tuple(property) # type: tuple
                for p, v in cursor.execute(query, params):  # --type: str, str
                    values[p] = v
                for p in property:  # --type: str
                    if p not in values:
                        values[p] = None
                return values
            else:
                query = '''
SELECT value FROM custom_command_properties 
    WHERE broadcaster=? AND permission=? AND command=? AND property=?'''
                cursor.execute(query, (broadcaster, permission,
                                       command.lower(), property))
                row = cursor.fetchone()  # type: Optional[Tuple[str]]
                return row and row[0]  # type: ignore

    def processCustomCommandProperty(self,
                                     broadcaster: str,
                                     permission: str,
                                     command: str,
                                     property: str,
                                     value=Optional[str]) -> bool:
        with closing(self.connection.cursor()) as cursor:  # --type: sqlite3.Cursor
            try:
                if value is None:
                    query = '''
DELETE FROM custom_command_properties
    WHERE broadcaster=? AND permission=? AND command=? AND property=?'''  # type: str
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

    def hasFeature(self,
                   broadcaster: str,
                   feature: str) -> bool:
        query = '''
SELECT 1 FROM chat_features WHERE broadcaster=? AND feature=?'''  # type: str
        with closing(self.connection.cursor()) as cursor:  # --type: sqlite3.Cursor
            cursor.execute(query, (broadcaster, feature))
            return cursor.fetchone() is not None

    def addFeature(self,
                   broadcaster: str,
                   feature: str) -> bool:
        query = '''
INSERT INTO chat_features (broadcaster, feature) VALUES (?, ?)'''  # type: str
        with closing(self.connection.cursor()) as cursor:  # --type: sqlite3.Cursor
            try:
                cursor.execute(query, (broadcaster, feature))
                self.connection.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def removeFeature(self,
                      broadcaster: str,
                      feature: str) -> bool:
        query = '''
DELETE FROM chat_features WHERE broadcaster=? AND feature=?'''  # type: str
        with closing(self.connection.cursor()) as cursor:  # --type: sqlite3.Cursor
            cursor.execute(query, (broadcaster, feature))
            self.connection.commit()
            return cursor.rowcount != 0
    
    def listBannedChannels(self) -> Iterable[str]:
        query = '''SELECT broadcaster FROM banned_channels'''  # type: str
        with closing(self.connection.cursor()) as cursor:  # --type: sqlite3.Cursor
            for broadcaster, in cursor.execute(query): # --type: str
                yield broadcaster

    def isChannelBannedReason(self, broadcaster: str) -> Optional[str]:
        query = '''
SELECT reason FROM banned_channels WHERE broadcaster=?'''  # type: str
        with closing(self.connection.cursor()) as cursor:  # --type: sqlite3.Cursor
            cursor.execute(query, (broadcaster,))
            row = cursor.fetchone()  # type: Optional[Tuple[str]]
            return row and row[0]  # type: ignore

    def addBannedChannel(self,
                         broadcaster: str,
                         reason: str,
                         nick: str) -> bool:
        query = '''
INSERT INTO banned_channels 
    (broadcaster, currentTime, reason, who)
    VALUES (?, CURRENT_TIMESTAMP, ?, ?)'''  # type: str
        history = '''
INSERT INTO banned_channels_log
    (broadcaster, currentTime, reason, who, actionLog) 
    VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?)'''  # type: str
        with closing(self.connection.cursor()) as cursor:  # --type: sqlite3.Cursor
            try:
                cursor.execute(query, (broadcaster, reason, nick))
                self.connection.commit()
            except sqlite3.IntegrityError:
                return False
            
            cursor.execute(history, (broadcaster, reason, nick, 'add'))
            self.connection.commit()
            return True

    def removeBannedChannel(self,
                            broadcaster: str,
                            reason: str,
                            nick: str) -> bool:
        query = '''
DELETE FROM banned_channels WHERE broadcaster=?'''  # type: str
        history = '''
INSERT INTO banned_channels_log
    (broadcaster, currentTime, reason, who, actionLog) 
    VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?)'''  # type: str
        with closing(self.connection.cursor()) as cursor:  # --type: sqlite3.Cursor
            cursor.execute(query, (broadcaster,))
            self.connection.commit()
            if cursor.rowcount == 0:
                return False

            cursor.execute(history, (broadcaster, reason, nick, 'remove'))
            self.connection.commit()
            return True

    def recordTimeout(self,
                      broadcaster: str,
                      user: str,
                      fromUser: Optional[str],
                      module: str,
                      level: Optional[int],
                      length: int,
                      message: Optional[str],
                      reason: Optional[str]) -> bool:
        attach = '''
ATTACH DATABASE ? AS timeout'''  # type: str
        query = '''
INSERT INTO timeout.timeout_logs 
    (broadcaster, twitchUser, fromUser, module, level, length, message, reason)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''  # type: str
        with closing(self.connection.cursor()) as cursor:  # --type: sqlite3.Cursor
            cursor.execute(attach, (self._timeoutlogfile,))
            try:
                cursor.execute(query, (broadcaster, user, fromUser, module,
                                       level, length, message, reason))
                self.connection.commit()
                return True
            except sqlite3.IntegrityError:
                return False
        
    def getChatProperty(self,
                        broadcaster: str,
                        property: str,
                        default: Any=None,
                        parse: Optional[Callable[[str], Any]]=None) -> Any:
        query = '''
SELECT value FROM chat_properties WHERE broadcaster=? AND property=?'''  # type: str
        with closing(self.connection.cursor()) as cursor:  # --type: sqlite3.Cursor
            cursor.execute(query, (broadcaster, property,))
            row = cursor.fetchone()  # type: Optional[Tuple[str]]
            if row is None:
                return default
            if parse is not None:
                return parse(row[0])
            return row[0]
    
    def getChatProperties(self,
                          broadcaster: str,
                          properties: Sequence[str],
                          default: Any=None,
                          parse: Any=None) -> Mapping[str, Any]:
        query = '''
SELECT property, value FROM chat_properties
    WHERE broadcaster=? AND property IN (%s)
''' % ','.join('?' * len(properties))  # type: str
        with closing(self.connection.cursor()) as cursor:  # --type: sqlite3.Cursor
            values = {}  # type: Dict[str, Any]
            params = (broadcaster,) + tuple(properties)
            for property, value in cursor.execute(query, params):
                if isinstance(parse, dict) and property in parse:
                    value = parse[property](value)
                if isinstance(parse, Callable):  # type: ignore
                    value = parse(value)  # type: ignore
                values[property] = value
            for property in properties:
                if property not in values:
                    if isinstance(default, dict) and property in default:
                        value = default[property]
                    else:
                        value = default
                    values[property] = value
            return values
    
    def setChatProperty(self,
                        broadcaster: str,
                        property: str,
                        value: Optional[str]=None) -> bool:
        with closing(self.connection.cursor()) as cursor:  # --type: sqlite3.Cursor
            if value is None:
                query = '''
DELETE FROM chat_properties WHERE broadcaster=? AND property=?'''  # type: str
                params = broadcaster, property,  # type: tuple
            else:
                query = '''
REPLACE INTO chat_properties (broadcaster, property, value) VALUES (?, ?, ?)'''
                params = broadcaster, property, value,
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.rowcount != 0
