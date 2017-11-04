from typing import Any, AsyncIterator, Callable, Dict, Mapping  # noqa: F401
from typing import Optional, Sequence, Tuple, TypeVar, Union  # noqa: F401
from typing import overload

import aioodbc.cursor  # noqa: F401

from ._base import Database

T = TypeVar('T')
S = TypeVar('S')


class ChatPropertiesMixin(Database):
    async def getAllChatProperties(self, broadcaster: str
                                   ) -> AsyncIterator[Tuple[str, str]]:
        query: str = '''
SELECT property, value FROM chat_properties WHERE broadcaster=?
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster,))
            property: str
            value: str
            async for property, value in cursor:
                yield property, value

    @overload
    async def getChatProperty(self,
                              broadcaster: str,
                              property: str) -> Optional[str]: ...
    @overload  # noqa: F811,E301
    async def getChatProperty(self,
                              broadcaster: str,
                              property: str,
                              default: T
                              ) -> Union[str, T]: ...
    @overload  # noqa: F811,E301
    async def getChatProperty(self,
                              broadcaster: str,
                              property: str,
                              default: T,
                              parse: Callable[[str], S]
                              ) -> Union[T, S]: ...
    async def getChatProperty(self,  # type: ignore  # noqa: F811,E301
                              broadcaster,
                              property,
                              default=None,
                              parse=None):
        query: str = '''
SELECT value FROM chat_properties WHERE broadcaster=? AND property=?'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster, property,))
            row: Optional[Tuple[str]] = await cursor.fetchone()
            if row is None:
                return default
            if parse is not None:
                return parse(row[0])
            return row[0]

    @overload
    async def getChatProperties(self,
                                broadcaster: str,
                                properties: Sequence[str]
                                ) -> Mapping[str, Optional[str]]: ...
    @overload  # noqa: F811,E301
    async def getChatProperties(self,
                                broadcaster: str,
                                properties: Sequence[str],
                                default: T
                                ) -> Mapping[str, Union[str, T]]: ...
    @overload  # noqa: F811,E301
    async def getChatProperties(self,
                                broadcaster: str,
                                properties: Sequence[str],
                                default: Mapping[str, T]
                                ) -> Mapping[str, Union[str, T]]: ...
    @overload  # noqa: F811,E301
    async def getChatProperties(self,
                                broadcaster: str,
                                properties: Sequence[str],
                                default: T,
                                parse: Mapping[str, Callable[[str], S]]
                                ) -> Mapping[str, Union[str, T, S]]: ...
    @overload  # noqa: F811,E301
    async def getChatProperties(self,
                                broadcaster: str,
                                properties: Sequence[str],
                                default: T,
                                parse: Callable[[str], S]
                                ) -> Mapping[str, Union[T, S]]: ...
    @overload  # noqa: F811,E301
    async def getChatProperties(self,
                                broadcaster: str,
                                properties: Sequence[str],
                                default: Mapping[str, T],
                                parse: Mapping[str, Callable[[str], S]]
                                ) -> Mapping[str, Union[str, T, S]]: ...
    @overload  # noqa: F811,E301
    async def getChatProperties(self,
                                broadcaster: str,
                                properties: Sequence[str],
                                default: Mapping[str, T],
                                parse: Callable[[str], S]
                                ) -> Mapping[str, Union[T, S]]: ...
    async def getChatProperties(self,  # type: ignore  # noqa: F811,E301
                                broadcaster,
                                properties,
                                default=None,
                                parse=None):
        query: str = '''
SELECT property, value FROM chat_properties
    WHERE broadcaster=? AND property IN (%s)
''' % ','.join('?' * len(properties))
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            values: Dict[str, Any] = {}
            params = (broadcaster,) + tuple(properties)
            async for property, value in await cursor.execute(query, params):
                if isinstance(parse, dict) and property in parse:
                    value = parse[property](value)
                if callable(parse):
                    value = parse(value)
                values[property] = value
            for property in properties:
                if property not in values:
                    if isinstance(default, dict):
                        if property in default:
                            value = default[property]
                        else:
                            continue
                    else:
                        value = default
                    values[property] = value
            return values

    async def setChatProperty(self,
                              broadcaster: str,
                              property: str,
                              value: Optional[str]=None) -> bool:
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            query: str
            params: Tuple[Any, ...]
            if value is None:
                query = '''
DELETE FROM chat_properties WHERE broadcaster=? AND property=?
'''
                params = broadcaster, property,
            else:
                if self.isSqlite:
                    query = '''
REPLACE INTO chat_properties (broadcaster, property, value) VALUES (?, ?, ?)
'''
                    params = broadcaster, property, value,
                else:
                    query = '''
INSERT INTO chat_properties (broadcaster, property, value) VALUES (?, ?, ?)
    ON CONFLICT ON CONSTRAINT chat_properties_pkey
    DO UPDATE SET value=?
'''
                    params = broadcaster, property, value, value,
            await cursor.execute(query, params)
            await self.commit()
            return cursor.rowcount != 0
