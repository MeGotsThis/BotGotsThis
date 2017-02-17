from typing import List, NamedTuple, Optional
import string

class ParsedPrefix(NamedTuple):
    servername: Optional[str]
    nick: Optional[str]
    user: Optional[str]
    host: Optional[str]

nickSpecials = ...  # type: str


class IrcMessagePrefix:
    def __init__(self,
                 servername: Optional[str]=None,
                 nick: Optional[str]=None,
                 user: Optional[str]=None,
                 host: Optional[str]=None) -> None: ...
    @classmethod
    def fromPrefix(cls, prefix: str) -> 'IrcMessagePrefix': ...
    @property
    def servername(self) -> Optional[str]: ...
    @property
    def nick(self) -> Optional[str]: ...
    @property
    def user(self) -> Optional[str]: ...
    @property
    def host(self) -> Optional[str]: ...
    def __str__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    @staticmethod
    def parse(params: str) -> ParsedPrefix: ...