from typing import List, NamedTuple, Optional  # noqa: F401
import string


class ParsedPrefix(NamedTuple):
    servername: Optional[str]
    nick: Optional[str]
    user: Optional[str]
    host: Optional[str]


nickSpecials: str = '-_'


class IrcMessagePrefix:
    __slots__ = ('_servername', '_nick', '_user', '_host')

    def __init__(self,
                 servername: Optional[str]=None,
                 nick: Optional[str]=None,
                 user: Optional[str]=None,
                 host: Optional[str]=None) -> None:
        if not isinstance(servername, (type(None), str)):
            raise TypeError()
        if not isinstance(nick, (type(None), str)):
            raise TypeError()
        if not isinstance(user, (type(None), str)):
            raise TypeError()
        if not isinstance(host, (type(None), str)):
            raise TypeError()

        if servername is None and nick is None:
            raise ValueError()
        if servername is not None:
            if nick is not None or user is not None or host is not None:
                raise ValueError()
            if not servername or any(c in ' \0\r\n' for c in servername):
                raise ValueError()
        if nick is not None:
            if not nick or any(c in ' \0\r\n' for c in nick):
                raise ValueError()
        if user is not None:
            if not user or any(c in ' \0\r\n' for c in user):
                raise ValueError()
        if host is not None:
            if not host or any(c in ' \0\r\n' for c in host):
                raise ValueError()

        self._servername: Optional[str] = servername
        self._nick: Optional[str] = nick
        self._user: Optional[str] = user
        self._host: Optional[str] = host

    @classmethod
    def fromPrefix(cls, prefix: str) -> 'IrcMessagePrefix':
        if not isinstance(prefix, str):
            raise TypeError()
        return cls(*cls.parse(prefix))

    @property
    def servername(self) -> Optional[str]:
        return self._servername

    @property
    def nick(self) -> Optional[str]:
        return self._nick

    @property
    def user(self) -> Optional[str]:
        return self._user

    @property
    def host(self) -> Optional[str]:
        return self._host

    def __str__(self) -> str:
        if self._servername is not None:
            return str(self._servername)
        if self._nick is not None:
            s: str = str(self._nick)
            if self._user is not None:
                s += '!' + self._user
            if self._host is not None:
                s += '@' + self._host
            return s
        return ''

    def __eq__(self, other: object) -> bool:
        if isinstance(other, IrcMessagePrefix):
            return (self._servername == other._servername
                    and self._nick == other._nick
                    and self._user == other._user
                    and self._host == other._host)
        return False

    def __ne__(self, other: object) -> bool:
        return not (self == other)

    @staticmethod
    def parse(params: str) -> ParsedPrefix:
        if not isinstance(params, str):
            raise TypeError()

        length: int = len(params)
        i: int = 0

        if i == length:
            raise ValueError()

        char: str
        ss: str
        s: List[str]
        u: List[str]
        h: List[str]
        servername: Optional[str] = None
        nick: Optional[str] = None
        user: Optional[str] = None
        host: Optional[str] = None
        isServerName: bool = False
        isNick: bool = False
        s = []
        while i < length:
            char = params[i]
            i += 1

            if char == '!':
                if isServerName:
                    raise ValueError()
                break
            if char == '@':
                if isServerName:
                    raise ValueError()
                break
            if not len(s):
                if char not in string.ascii_letters and not char.isdigit():
                    raise ValueError()
                s.append(char)
            else:
                if (char in string.ascii_letters or char.isdigit()
                        or char == '-'):
                    s.append(char)
                elif char in nickSpecials:
                    if isServerName:
                        raise ValueError()
                    s.append(char)
                    isNick = True
                elif char == '.':
                    if isNick:
                        raise ValueError()
                    s.append(char)
                    isServerName = True
                else:
                    raise ValueError()
        if isServerName and isNick:
            raise ValueError()
        if len(s) == 0:
            raise ValueError()
        if char == '.':
            raise ValueError()
        ss = ''.join(s)
        if isServerName:
            servername = ss
        else:
            nick = ss

        if char == '!':
            u = []
            while i < length:
                char = params[i]
                i += 1

                if char == '@':
                    break
                if char == '.':
                    raise ValueError()
                if char in ' \0\r\n':
                    raise ValueError()
                u.append(char)
            if len(u) == 0:
                raise ValueError()
            user = ''.join(u)

        if char == '@':
            h = []
            s = []
            while i < length:
                char = params[i]
                i += 1

                if char == '.':
                    if len(s) == 0:
                        raise ValueError()
                    if s[-1] == '-':
                        raise ValueError()
                    if not s[0].isalpha() and not s[0].isdigit():
                        raise ValueError()
                    s.append(char)
                    h.extend(s)
                    s = []
                else:
                    if not char.isalnum() and char != '-' and char != '_':
                        raise ValueError()
                    s.append(char)

            if len(s) == 0:
                raise ValueError()
            if s[-1] == '-':
                raise ValueError()
            if not s[0].isalpha() and not s[0].isdigit():
                raise ValueError()
            h.extend(s)

            host = ''.join(h)

        if i != length:
            raise ValueError()

        return ParsedPrefix(servername, nick, user, host)
