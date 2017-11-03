import json
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, TypeVar  # noqa: F401,E501
from typing import Union, overload

from ._abc import AbcCacheStore
from .. import database

T = TypeVar('T')
S = TypeVar('S')


class ChatPropertiesMixin(AbcCacheStore):
    def __init__(self) -> None:
        super().__init__()
        self._chatProperties: Dict[str, Dict[str, str]] = {}

    def _propertiesKey(self, broadcaster: str) -> str:
        return f'twitch:{broadcaster}:properties'

    async def loadChatProperties(self, broadcaster: str) -> Dict[str, str]:
        key: str = self._propertiesKey(broadcaster)
        properties: Dict[str, str]
        db: database.DatabaseMain
        async with database.get_main_database() as db:
            properties = {property: value async for (property, value)
                          in db.getAllChatProperties(broadcaster)}
        await self.redis.setex(key, 3600, json.dumps(properties))
        return properties

    async def _getChatProperties(self, broadcaster: str) -> Dict[str, str]:
        if broadcaster not in self._chatProperties:
            key: str = self._propertiesKey(broadcaster)
            value: Optional[str] = await self.redis.get(key)
            if value is None:
                data: Dict[str, str]
                data = await self.loadChatProperties(broadcaster)
                self._chatProperties[broadcaster] = data
            else:
                self._chatProperties[broadcaster] = json.loads(value)
        return self._chatProperties[broadcaster]

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
        properties: Dict[str, str] = await self._getChatProperties(broadcaster)
        if property not in properties:
            return default
        if callable(parse):
            return parse(properties[property])
        return properties[property]

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
        chatProperties: Dict[str, str]
        chatProperties = await self._getChatProperties(broadcaster)
        values: Dict[str, Any] = {}
        property: str
        for property in properties:
            value: Any
            if property in chatProperties:
                value = chatProperties[property]
                if callable(parse):
                    value = parse(value)
                elif isinstance(parse, dict) and property in parse:
                    value = parse[property](chatProperties[property])
                values[property] = value
            else:
                if isinstance(default, dict):
                    if property in default:
                        value = default[property]
                    else:
                        continue
                else:
                    value = default
            values[property] = value
        return values

    async def resetChatProperties(self, broadcaster: str) -> None:
        key: str = self._propertiesKey(broadcaster)
        await self.redis.delete(key)
        if broadcaster in self._chatProperties:
            del self._chatProperties[broadcaster]

    async def setChatProperty(self,
                              broadcaster: str,
                              property: str,
                              value: Optional[str]=None) -> bool:
        val: bool
        db: database.DatabaseMain
        async with database.get_main_database() as db:
            val = await db.setChatProperty(broadcaster, property, value)
        if val:
            await self.resetChatProperties(broadcaster)
        return val
