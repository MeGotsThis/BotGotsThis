# from bot.data import Channel
from .message import Message
# from .permissions import ChatPermissionSet, WhisperPermissionSet
# from ..database import DatabaseMain
from bot.twitchmessage import IrcMessageTagsReadOnly
from datetime import datetime
from typing import Any, Awaitable, Callable, Iterable, List, NamedTuple
from typing import Optional, Union


Send = Callable[[Union[str, Iterable[str]]], None]


class ChatCommandArgs(NamedTuple):
    database: Any  # DatabaseMain
    chat: Any  # Channel
    tags: IrcMessageTagsReadOnly
    nick: str
    message: Message
    permissions: Any  # ChatPermissionSet
    timestamp: datetime


class WhisperCommandArgs(NamedTuple):
    database: Any  # DatabaseMain
    nick: str
    message: Message
    permissions: Any  # WhisperPermissionSet
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
    permissions: Any  # ChatPermissionSet
    timestamp: datetime


class CustomProcessArgs(NamedTuple):
    database: Any  # DatabaseMain
    chat: Any  # Channel
    tags: IrcMessageTagsReadOnly
    nick: str
    permissions: Any  # ChatPermissionSet
    broadcaster: str
    level: str
    command: str
    messages: List[str]


class ManageBotArgs(NamedTuple):
    database: Any  # DatabaseMain
    permissions: Any  # Union[ChatPermissionSet, WhisperPermissionSet]
    send: Send
    nick: str
    message: Message


ChatCommand = Callable[[ChatCommandArgs], Awaitable[bool]]

WhisperCommand = Callable[[WhisperCommandArgs], Awaitable[bool]]

CustomCommandField = Callable[[CustomFieldArgs], Awaitable[Optional[str]]]

CustomCommandProcess = Callable[[CustomProcessArgs], Awaitable[None]]

ManageBotCommand = Callable[[ManageBotArgs], Awaitable[bool]]


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
    format: Optional[str]  # noqa: E701
    prefix: Optional[str]
    suffix: Optional[str]
    param: Optional[str]
    default: Optional[str]
    original: Optional[str]
