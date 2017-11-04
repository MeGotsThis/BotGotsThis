from typing import Any, AsyncIterator, Dict, Optional, Tuple  # noqa: F401

import aioodbc.cursor  # noqa: F401
import pyodbc

from ._base import Database
from .. import data


class CustomCommandsMixin(Database):
    async def getAutoJoinsChats(self) -> 'AsyncIterator[data.AutoJoinChannel]':
        query: str = '''
SELECT broadcaster, priority, cluster FROM auto_join ORDER BY priority ASC
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            r: Tuple[Any, ...]
            async for r in await cursor.execute(query):
                yield data.AutoJoinChannel(*r)

    async def getChatCommands(self,
                              broadcaster: str,
                              command: str) -> Dict[str, Dict[str, str]]:
        query: str = '''
SELECT broadcaster, permission, fullMessage
    FROM custom_commands WHERE broadcaster IN (?, \'#global\') AND command=?
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            commands: Dict[str, Dict[str, str]]
            commands = {broadcaster: {}, '#global': {}}
            params: Tuple[Any, ...] = (broadcaster, command)
            row: Optional[Tuple[str, str, str]]
            async for row in await cursor.execute(query, params):
                commands[row[0]][row[1]] = row[2]
            return commands

    async def getCustomCommands(self, broadcaster: str
                                ) -> AsyncIterator[Tuple[str, str, str]]:
        query: str = '''
SELECT command, permission, fullMessage FROM custom_commands
    WHERE broadcaster=?
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster,))
            command: str
            permission: str
            message: str
            async for command, permission, message in cursor:
                yield command, permission, message

    async def getCustomCommand(self,
                               broadcaster: str,
                               permission: str,
                               command: str) -> Optional[str]:
        find: str = '''
SELECT fullMessage FROM custom_commands
    WHERE broadcaster=? AND permission=? AND command=?
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(find, (broadcaster, permission,
                                        command.lower()))
            row: Optional[Tuple[str]] = await cursor.fetchone()
            return row and row[0]

    async def insertCustomCommand(self,
                                  broadcaster: str,
                                  permission: str,
                                  command: str,
                                  fullMessage: str,
                                  user: str) -> bool:
        query: str = '''
INSERT INTO custom_commands
    (broadcaster, permission, command, commandDisplay, fullMessage, creator,
    created, lastEditor, lastUpdated)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, CURRENT_TIMESTAMP)
'''
        history: str = '''
INSERT INTO custom_commands_history
    (broadcaster, permission, command, commandDisplay, process, fullMessage,
    creator, created)
    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            try:
                lower: str = command.lower()
                display: Optional[str] = None
                if lower != command:
                    display = command
                await cursor.execute(query, (broadcaster, permission, lower,
                                             display, fullMessage, user, user))
            except pyodbc.Error:
                return False

            await cursor.execute(history, (broadcaster, permission, lower,
                                           display, 'add', fullMessage, user))
            await self.commit()
            return True

    async def updateCustomCommand(self,
                                  broadcaster: str,
                                  permission: str,
                                  command: str,
                                  fullMessage: str,
                                  user: str) -> bool:
        query: str = '''
UPDATE custom_commands
    SET commandDisplay=?, fullMessage=?, lastEditor=?,
        lastUpdated=CURRENT_TIMESTAMP
    WHERE broadcaster=? AND permission=? AND command=?
'''
        history: str = '''
INSERT INTO custom_commands_history
    (broadcaster, permission, command, commandDisplay, process, fullMessage,
    creator, created)
    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            display: Optional[str] = None
            if command.lower() != command:
                display = command
            await cursor.execute(query, (display, fullMessage, user,
                                         broadcaster, permission,
                                         command.lower()))
            if cursor.rowcount == 0:
                return False

            await cursor.execute(history, (broadcaster, permission,
                                           command.lower(), display, 'edit',
                                           fullMessage, user))
            await self.commit()
            return True

    async def replaceCustomCommand(self,
                                   broadcaster: str,
                                   permission: str,
                                   command: str,
                                   fullMessage: str,
                                   user: str) -> bool:
        query: str
        params: Tuple[Any, ...]
        history: str = '''
INSERT INTO custom_commands_history
    (broadcaster, permission, command, commandDisplay, process, fullMessage,
    creator, created)
    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            display: Optional[str] = None
            if command.lower() != command:
                display = command
            if self.isSqlite:
                query = '''
REPLACE INTO custom_commands
    (broadcaster, permission, command, commandDisplay, fullMessage, creator,
    created, lastEditor, lastUpdated)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, CURRENT_TIMESTAMP)
'''
                params = (broadcaster, permission, command.lower(), display,
                          fullMessage, user, user)
            else:
                query = '''
INSERT INTO custom_commands
    (broadcaster, permission, command, commandDisplay, fullMessage, creator,
    created, lastEditor, lastUpdated)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, CURRENT_TIMESTAMP)
    ON CONFLICT ON CONSTRAINT custom_commands_pkey
    DO UPDATE SET commandDisplay=?, fullMessage=?, creator=?,
        created=CURRENT_TIMESTAMP, lastEditor=?, lastUpdated=CURRENT_TIMESTAMP
'''
                params = (broadcaster, permission, command.lower(), display,
                          fullMessage, user, user, display, fullMessage, user,
                          user)
            await cursor.execute(query, params)
            if cursor.rowcount == 0:
                return False

            await cursor.execute(history, (broadcaster, permission,
                                           command.lower(), display, 'replace',
                                           fullMessage, user))
            await self.commit()
            return True

    async def appendCustomCommand(self,
                                  broadcaster: str,
                                  permission: str,
                                  command: str,
                                  message: str,
                                  user: str) -> bool:
        find: str = '''
SELECT fullMessage FROM custom_commands
    WHERE broadcaster=? AND permission=? AND command=?
'''
        query: str = '''
UPDATE custom_commands
    SET fullMessage=?, lastEditor=?, lastUpdated=CURRENT_TIMESTAMP
    WHERE broadcaster=? AND permission=? AND command=?
'''
        history: str = '''
INSERT INTO custom_commands_history
    (broadcaster, permission, command, commandDisplay, process, fullMessage,
    creator, created)
    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(find, (broadcaster, permission,
                                        command.lower()))
            original: Optional[Tuple[str]] = await cursor.fetchone()
            if original is None:
                return False
            fullMessage: str = original[0] + message

            display: Optional[str] = None
            if command.lower() != command:
                display = command
            await cursor.execute(query, (fullMessage, user, broadcaster,
                                         permission, command.lower()))
            if cursor.rowcount == 0:
                return False

            await cursor.execute(history, (broadcaster, permission,
                                           command.lower(), display, 'append',
                                           fullMessage, user))
            await self.commit()
            return True

    async def deleteCustomCommand(self,
                                  broadcaster: str,
                                  permission: str,
                                  command: str,
                                  user: str) -> bool:
        query: str = '''
DELETE FROM custom_commands
    WHERE broadcaster=? AND permission=? AND command=?
'''
        history: str = '''
INSERT INTO custom_commands_history
    (broadcaster, permission, command, commandDisplay, process, fullMessage,
    creator, created)
    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster, permission,
                                         command.lower()))

            if cursor.rowcount == 0:
                return False

            display: Optional[str] = None
            if command.lower() != command:
                display = command
            await cursor.execute(history, (broadcaster, permission,
                                           command.lower(), display, 'delete',
                                           None, user))
            await self.commit()
            return True

    async def levelCustomCommand(self,
                                 broadcaster: str,
                                 permission: str,
                                 command: str,
                                 user: str,
                                 new_permission: str) -> bool:
        query: str = '''
UPDATE custom_commands SET permission=?
    WHERE broadcaster=? AND permission=? AND command=?
'''
        history: str = '''
INSERT INTO custom_commands_history
    (broadcaster, permission, command, commandDisplay, process, fullMessage,
    creator, created)
    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            try:
                await cursor.execute(query, (new_permission, broadcaster,
                                             permission, command.lower()))
            except pyodbc.Error:
                return False

            if cursor.rowcount == 0:
                return False

            display: Optional[str] = None
            if command.lower() != command:
                display = command
            await cursor.execute(history, (broadcaster, new_permission,
                                           command.lower(), display, 'level',
                                           permission, user))
            await self.commit()
            return True

    async def renameCustomCommand(self,
                                  broadcaster: str,
                                  permission: str,
                                  command: str,
                                  user: str,
                                  new_command: str) -> bool:
        query: str = '''
UPDATE custom_commands SET command=?, commandDisplay=?
    WHERE broadcaster=? AND permission=? AND command=?
'''
        history: str = '''
INSERT INTO custom_commands_history
    (broadcaster, permission, command, commandDisplay, process, fullMessage,
    creator, created)
    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            display: Optional[str] = None
            if new_command.lower() != new_command:
                display = new_command
            try:
                await cursor.execute(query, (new_command.lower(), display,
                                             broadcaster, permission,
                                             command.lower()))
            except pyodbc.Error:
                return False

            if cursor.rowcount == 0:
                return False

            await cursor.execute(history, (broadcaster, permission,
                                           new_command.lower(), display,
                                           'rename', command.lower(), user))
            await self.commit()
            return True

    async def getCustomCommandProperties(
            self, broadcaster: str
            ) -> AsyncIterator[Tuple[str, str, str, str]]:
        query: str = '''
SELECT command, permission, property, value FROM custom_command_properties
    WHERE broadcaster=?
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster,))
            command: str
            permission: str
            property: str
            value: str
            async for command, permission, property, value in cursor:
                yield command, permission, property, value

    async def getCustomCommandProperty(
            self,
            broadcaster: str,
            permission: str,
            command: str,
            property: 'Optional[data.CommandProperty]'=None
            ) -> 'Optional[data.CommandReturn]':
        query: str
        cursor: aioodbc.cursor.Cursor
        p: str
        v: str
        params: Tuple[Any, ...]
        values: Dict[str, str]
        async with await self.cursor() as cursor:
            if property is None:
                query = '''
SELECT property, value FROM custom_command_properties
    WHERE broadcaster=? AND permission=? AND command=?
'''
                values = {}
                params = (broadcaster, permission, command.lower())
                async for p, v in await cursor.execute(query, params):
                    values[p] = v
                return values
            elif isinstance(property, list):
                query = '''
SELECT property, value FROM custom_command_properties
    WHERE broadcaster=? AND permission=? AND command=?
        AND property IN (%s)
''' % ','.join('?' * len(property))
                values = {}
                params = (broadcaster, permission, command.lower(),
                          ) + tuple(property)
                async for p, v in await cursor.execute(query, params):
                    values[p] = v
                for p in property:
                    if p not in values:
                        values[p] = None
                return values
            else:
                query = '''
SELECT value FROM custom_command_properties
    WHERE broadcaster=? AND permission=? AND command=? AND property=?
'''
                await cursor.execute(query, (broadcaster, permission,
                                             command.lower(), property))
                row: Optional[Tuple[str]] = await cursor.fetchone()
                return row and row[0]

    async def processCustomCommandProperty(self,
                                           broadcaster: str,
                                           permission: str,
                                           command: str,
                                           property: str,
                                           value: Optional[str]=None) -> bool:
        query: str
        params: Tuple[Any, ...]
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            try:
                if value is None:
                    query = '''
DELETE FROM custom_command_properties
    WHERE broadcaster=? AND permission=? AND command=? AND property=?
'''
                    params = broadcaster, permission, command.lower(), property
                else:
                    if self.isSqlite:
                        query = '''
REPLACE INTO custom_command_properties
    (broadcaster, permission, command, property, value)
    VALUES (?, ?, ?, ?, ?)
'''
                        params = (broadcaster, permission, command.lower(),
                                  property, value)
                    else:
                        query = '''
INSERT INTO custom_command_properties
    (broadcaster, permission, command, property, value)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT ON CONSTRAINT custom_command_properties_pkey
    DO UPDATE SET value=?
'''
                        params = (broadcaster, permission, command.lower(),
                                  property, value, value)
                await cursor.execute(query, params)
                await self.commit()
                return cursor.rowcount != 0
            except pyodbc.Error:
                return False
