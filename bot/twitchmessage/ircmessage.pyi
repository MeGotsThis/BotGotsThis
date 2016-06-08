from .ircparams import IrcMessageParams
from .ircprefix import IrcMessagePrefix
from .irctags import IrcMessageTagsReadOnly
from typing import NamedTuple, Optional, Union

Command = Union[str, int]

ParsedMessage = NamedTuple('ParsedMessage',
                           [('tags', Optional[IrcMessageTagsReadOnly]),
                            ('prefix', Optional[IrcMessagePrefix]),
                            ('command', Command),
                            ('params', IrcMessageParams)])


class IrcMessage:
    def __init__(self,
                 tags:Optional[IrcMessageTagsReadOnly]=None,
                 prefix:Optional[IrcMessagePrefix]=None,
                 command:Command=None,
                 params:IrcMessageParams=None) -> None: ...
    @classmethod
    def fromMessage(cls, message:str) -> 'IrcMessage': ...
    @property
    def tags(self) -> Optional[IrcMessageTagsReadOnly]: ...
    @property
    def prefix(self) -> Optional[IrcMessagePrefix]: ...
    @property
    def command(self) -> Command: ...
    @property
    def params(self) -> IrcMessageParams: ...
    def __str__(self) -> str: ...
    def __eq__(self, other:object) -> bool: ...
    def __ne__(self, other:object) -> bool: ...
    @staticmethod
    def parse(message:str) -> ParsedMessage: ...