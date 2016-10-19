from .message import Message
from .permissions import ChatPermissionSet, WhisperPermissionSet
from ..database import DatabaseBase
from bot.twitchmessage import IrcMessageTagsReadOnly
from datetime import datetime
from typing import Any, Callable, Iterable, List, NamedTuple, Optional, Union

ChatCommandArgs = NamedTuple('ChatCommandArgs',
                             [('database', DatabaseBase),
                              ('chat', Any),
                              ('tags', IrcMessageTagsReadOnly),
                              ('nick', str),
                              ('message', Message),
                              ('permissions', ChatPermissionSet),
                              ('timestamp', datetime)])

WhisperCommandArgs = NamedTuple('WhisperCommandArgs',
                                [('database', DatabaseBase),
                                 ('nick', str),
                                 ('message', Message),
                                 ('permissions', WhisperPermissionSet),
                                 ('timestamp', datetime)])

CustomFieldArgs = NamedTuple('CustomFieldArgs',
                             [('field', str),
                              ('param', Optional[str]),
                              ('prefix', Optional[str]),
                              ('suffix', Optional[str]),
                              ('default', Optional[str]),
                              ('message', Message),
                              ('channel', str),
                              ('nick', str),
                              ('permissions', ChatPermissionSet),
                              ('timestamp', datetime)])

CustomProcessArgs = NamedTuple('CustomProcessArgs',
                               [('database', DatabaseBase),
                                ('chat', Any),
                                ('tags', IrcMessageTagsReadOnly),
                                ('nick', str),
                                ('permissions', ChatPermissionSet),
                                ('broadcaster', str),
                                ('level', str),
                                ('command', str),
                                ('messages', List[str])])

ManageBotArgs = NamedTuple('ManageBotArgs',
                           [('database', DatabaseBase),
                            ('permissions', Union[WhisperPermissionSet,
                                                  ChatPermissionSet]),
                            ('send', Callable[[Union[str,Iterable[str]]], None]),
                            ('nick', str),
                            ('message', Message)])

ChatCommand = Callable[[ChatCommandArgs], bool]

WhisperCommand = Callable[[WhisperCommandArgs], bool]

CustomCommandField = Callable[[CustomFieldArgs], Optional[str]]

CustomCommandProcess = Callable[[CustomProcessArgs], None]

ManageBotCommand = Callable[[ManageBotArgs], bool]

Send = Callable[[Union[str,Iterable[str]]], None]

CustomCommand = NamedTuple('CustomCommand',
                           [('message', str),
                            ('broadcaster', str),
                            ('level', str)])

CommandActionTokens = NamedTuple('CommandActionTokens',
                                 [('action', str),
                                  ('broadcaster', str),
                                  ('level', Optional[str]),
                                  ('command', str),
                                  ('text', str)])

CustomFieldParts = NamedTuple('CustomFieldParts',
                              [('plainText', str),
                               ('field', Optional[str]),
                               ('format', Optional[str]),
                               ('prefix', Optional[str]),
                               ('suffix', Optional[str]),
                               ('param', Optional[str]),
                               ('default', Optional[str]),
                               ('original', Optional[str])])
