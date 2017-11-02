import asyncio
import json
from typing import Dict, List, Optional, Tuple  # noqa: F401

from ._abc import AbcCacheStore
from .. import database

CommandData = Tuple[str, Dict[str, str]]
CommandDict = Dict[str, CommandData]
CommandsDict = Dict[str, CommandDict]


class CustomCommandsMixin(AbcCacheStore):
    def _customCommandsKey(self, broadcaster: str) -> str:
        return f'twitch:{broadcaster}:commands'

    async def _getCustomCommands(self,
                                 broadcaster: str,
                                 db: database.DatabaseMain
                                 ) -> List[Tuple[str, str, str]]:
        return [row async for row in db.getCustomCommands(broadcaster)]

    async def _getCustomCommandProperties(self,
                                          broadcaster: str,
                                          db: database.DatabaseMain
                                          ) -> List[Tuple[str, str, str, str]]:
        return [row async for row
                in db.getCustomCommandProperties(broadcaster)]

    async def loadCustomCommands(self, broadcaster: str) -> CommandsDict:
        key: str = self._customCommandsKey(broadcaster)
        commands: CommandsDict = {}
        commandData: List[Tuple[str, str, str]]
        propertyData: List[Tuple[str, str, str, str]]
        db: database.DatabaseMain
        async with database.get_main_database() as db:
            commandData, propertyData = await asyncio.gather(
                self._getCustomCommands(broadcaster, db),
                self._getCustomCommandProperties(broadcaster, db),
            )
        for command, permission, message in commandData:
            if command not in commands:
                commands[command] = {}
            commands[command][permission] = message, {}
        for command, permission, property, value in propertyData:
            commands[command][permission][1][property] = value
        timeout: int = 600 if broadcaster != '#global' else 3600
        await self.redis.setex(key, timeout, json.dumps(commands))
        return commands

    async def _getCommands(self, broadcaster: str) -> CommandsDict:
        key: str = self._customCommandsKey(broadcaster)
        value: Optional[str] = await self.redis.get(key)
        if value is None:
            return await self.loadCustomCommands(broadcaster)
        else:
            return json.loads(value)

    async def getChatCommands(self,
                              broadcaster: str,
                              command: str) -> Dict[str, Dict[str, str]]:
        cmdData: Dict[str, CommandsDict] = {}
        cmdData[broadcaster], cmdData['#global'] = await asyncio.gather(
            self._getCommands(broadcaster),
            self._getCommands('#global'),
        )
        commands: Dict[str, Dict[str, str]] = {
            broadcaster: {},
            '#global': {},
        }
        key: str
        commandData: CommandsDict
        for key, commandData in cmdData.items():
            if command in commandData:
                commands[key] = {
                    level: message
                    for (level, (message, properties),)
                    in commandData[command].items()
                }
        return commands

    async def getCustomCommand(self,
                               broadcaster: str,
                               permission: str,
                               command: str) -> Optional[str]:
        commandData: CommandsDict = await self._getCommands(broadcaster)
        if command not in commandData:
            return None
        if permission not in commandData[command]:
            return None
        return commandData[command][permission][0]

    async def getCustomCommandProperty(
            self,
            broadcaster: str,
            permission: str,
            command: str,
            property: Optional[database.CommandProperty]=None
            ) -> Optional[database.CommandReturn]:
        commandData: CommandsDict = await self._getCommands(broadcaster)
        if property is None:
            if command not in commandData:
                return {}
            if permission not in commandData[command]:
                return {}
            return dict(commandData[command][permission][1])
        elif not isinstance(property, str):
            if command not in commandData:
                return {}
            if permission not in commandData[command]:
                return {}
            properties: Dict[str, str] = commandData[command][permission][1]
            return {p: properties[p] if p in properties else None
                    for p in property}
        else:
            if command not in commandData:
                return None
            if permission not in commandData[command]:
                return None
            if property not in commandData[command][permission][1]:
                return None
            return commandData[command][permission][1][property]

    async def resetCustomCommands(self, broadcaster: str) -> None:
        key: str = self._customCommandsKey(broadcaster)
        await self.redis.delete(key)

    async def insertCustomCommand(self,
                                  broadcaster: str,
                                  permission: str,
                                  command: str,
                                  fullMessage: str,
                                  user: str) -> bool:
        val: bool
        db: database.DatabaseMain
        async with database.get_main_database() as db:
            val = await db.insertCustomCommand(
                broadcaster, permission, command, fullMessage, user)
        if val:
            await self.resetCustomCommands(broadcaster)
        return val

    async def updateCustomCommand(self,
                                  broadcaster: str,
                                  permission: str,
                                  command: str,
                                  fullMessage: str,
                                  user: str) -> bool:
        val: bool
        db: database.DatabaseMain
        async with database.get_main_database() as db:
            val = await db.updateCustomCommand(
                broadcaster, permission, command, fullMessage, user)
        if val:
            await self.resetCustomCommands(broadcaster)
        return val

    async def appendCustomCommand(self,
                                  broadcaster: str,
                                  permission: str,
                                  command: str,
                                  message: str,
                                  user: str) -> bool:
        val: bool
        db: database.DatabaseMain
        async with database.get_main_database() as db:
            val = await db.appendCustomCommand(
                broadcaster, permission, command, message, user)
        if val:
            await self.resetCustomCommands(broadcaster)
        return val

    async def replaceCustomCommand(self,
                                   broadcaster: str,
                                   permission: str,
                                   command: str,
                                   fullMessage: str,
                                   user: str) -> bool:
        val: bool
        db: database.DatabaseMain
        async with database.get_main_database() as db:
            val = await db.replaceCustomCommand(
                broadcaster, permission, command, fullMessage, user)
        if val:
            await self.resetCustomCommands(broadcaster)
        return val

    async def deleteCustomCommand(self,
                                  broadcaster: str,
                                  permission: str,
                                  command: str,
                                  user: str) -> bool:
        val: bool
        db: database.DatabaseMain
        async with database.get_main_database() as db:
            val = await db.deleteCustomCommand(
                broadcaster, permission, command, user)
        if val:
            await self.resetCustomCommands(broadcaster)
        return val

    async def levelCustomCommand(self,
                                 broadcaster: str,
                                 permission: str,
                                 command: str,
                                 user: str,
                                 new_permission: str) -> bool:
        val: bool
        db: database.DatabaseMain
        async with database.get_main_database() as db:
            val = await db.levelCustomCommand(
                broadcaster, permission, command, user, new_permission)
        if val:
            await self.resetCustomCommands(broadcaster)
        return val

    async def renameCustomCommand(self,
                                  broadcaster: str,
                                  permission: str,
                                  command: str,
                                  user: str,
                                  new_command: str) -> bool:
        val: bool
        db: database.DatabaseMain
        async with database.get_main_database() as db:
            val = await db.renameCustomCommand(
                broadcaster, permission, command, user, new_command)
        if val:
            await self.resetCustomCommands(broadcaster)
        return val

    async def processCustomCommandProperty(self,
                                           broadcaster: str,
                                           permission: str,
                                           command: str,
                                           property: str,
                                           value: Optional[str]=None) -> bool:
        val: bool
        db: database.DatabaseMain
        async with database.get_main_database() as db:
            val = await db.processCustomCommandProperty(
                broadcaster, permission, command, property, value)
        if val:
            await self.resetCustomCommands(broadcaster)
        return val
