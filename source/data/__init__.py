from .message import Message
from .permissions import ChatPermissionSet, WhisperPermissionSet
from ..database import DatabaseBase
from bot.twitchmessage import IrcMessageTagsReadOnly
from datetime import datetime
from typing import Any, Awaitable, Callable, Iterable, List, NamedTuple
from typing import Optional, Union

class ChatCommandArgs(NamedTuple):
    database: DatabaseBase
    chat: Any
    tags: IrcMessageTagsReadOnly
    nick: str
    message: Message
    permissions: ChatPermissionSet
    timestamp: datetime


class WhisperCommandArgs(NamedTuple):
    database: DatabaseBase
    nick: str
    message: Message
    permissions: WhisperPermissionSet
    timestamp: datetime


class CustomFieldArgs(NamedTuple):
    field: str
    param: Optional[str]
    prefix: Optional[str]
    suffix: Optional[str]
    default: Optional[str]
    message: Message
    channel: str
    nick: str
    permissions: ChatPermissionSet
    timestamp: datetime


class CustomProcessArgs(NamedTuple):
    database: DatabaseBase
    chat: Any
    tags: IrcMessageTagsReadOnly
    nick: str
    permissions: ChatPermissionSet
    broadcaster: str
    level: str
    command: str
    messages: List[str]


class ManageBotArgs(NamedTuple):
    database: DatabaseBase
    permissions: Union[WhisperPermissionSet, ChatPermissionSet]
    send: Callable[[Union[str,Iterable[str]]], None]
    nick: str
    message: Message


ChatCommand = Callable[[ChatCommandArgs], Awaitable[bool]]

WhisperCommand = Callable[[WhisperCommandArgs], bool]

CustomCommandField = Callable[[CustomFieldArgs], Optional[str]]

CustomCommandProcess = Callable[[CustomProcessArgs], None]

ManageBotCommand = Callable[[ManageBotArgs], bool]

Send = Callable[[Union[str,Iterable[str]]], None]


class CustomCommand(NamedTuple):
    message: str
    broadcaster: str
    level: str


class CommandActionTokens(NamedTuple):
    action: str
    broadcaster: str
    level: Optional[str]
    command: str
    text: str


class CustomFieldParts(NamedTuple):
    plainText: str
    field: Optional[str]
    format: Optional[str]
    prefix: Optional[str]
    suffix: Optional[str]
    param: Optional[str]
    default: Optional[str]
    original: Optional[str]
