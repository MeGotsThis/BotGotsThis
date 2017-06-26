from ._ircparams import IrcMessageParams
from ._ircprefix import IrcMessagePrefix, nickSpecials
from ._irctags import IrcMessageTagsReadOnly, IrcMessageTags, IrcMessageTagsKey
from ._irctags import TagValue, unescapedValue  # noqa: F401
from typing import List, NamedTuple, Optional, Union  # noqa: F401
import string

Command = Union[str, int]


class ParsedMessage(NamedTuple):
    tags: Optional[IrcMessageTagsReadOnly]
    prefix: Optional[IrcMessagePrefix]
    command: Command
    params: IrcMessageParams


class IrcMessage:
    __slots__ = ('_tags', '_prefix', '_command', '_params')

    def __init__(self,
                 tags: Optional[IrcMessageTagsReadOnly]=None,
                 prefix: Optional[IrcMessagePrefix]=None,
                 command: Command=0,
                 params: IrcMessageParams=IrcMessageParams()) -> None:
        if isinstance(tags, IrcMessageTagsReadOnly):
            tags = IrcMessageTagsReadOnly(tags)
        elif tags is not None:
            raise TypeError()
        if not isinstance(prefix, (type(None), IrcMessagePrefix)):
            raise TypeError()
        if isinstance(command, str):
            if not command.isalpha():
                raise ValueError()
        elif isinstance(command, int):
            if not (0 <= command <= 999):
                raise ValueError()
        else:
            raise TypeError()
        if not isinstance(params, IrcMessageParams):
            raise TypeError()

        self._tags: Optional[IrcMessageTagsReadOnly] = tags
        self._prefix: Optional[IrcMessagePrefix] = prefix
        self._command: Command = command
        self._params: IrcMessageParams = params

    @classmethod
    def fromMessage(cls, message: str) -> 'IrcMessage':
        if not isinstance(message, str):
            raise TypeError()
        return cls(*cls.parse(message))

    @property
    def tags(self) -> Optional[IrcMessageTagsReadOnly]:
        return self._tags

    @property
    def prefix(self) -> Optional[IrcMessagePrefix]:
        return self._prefix

    @property
    def command(self) -> Command:
        return self._command

    @property
    def params(self) -> IrcMessageParams:
        return self._params

    def __str__(self) -> str:
        message: str = ''
        if self._tags is not None:
            message += '@' + str(self._tags) + ' '
        if self._prefix is not None:
            message += ':' + str(self._prefix) + ' '
        if isinstance(self._command, int):
            message += str(self._command).rjust(3, '0')
        else:
            message += str(self._command)
        if not self._params.isEmpty:
            message += ' ' + str(self._params)
        return message

    def __eq__(self, other: object) -> bool:
        if isinstance(other, IrcMessage):
            return (self._tags == other._tags
                    and self._prefix == other._prefix
                    and self._command == other._command
                    and self._params == other._params)
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @staticmethod
    def parse(message: str) -> ParsedMessage:
        if not isinstance(message, str):
            raise TypeError()

        length: int = len(message)
        i: int = 0

        if i == length:
            raise ValueError()

        tags: Optional[IrcMessageTags] = None
        prefix: Optional[IrcMessagePrefix] = None
        command: Command
        params: IrcMessageParams

        # Tags
        v: List[str]
        s: List[str]
        isVendor: bool
        isKey: bool
        key: str
        vendor: Optional[str]
        value: TagValue
        tagkey: IrcMessageTagsKey
        char: str = message[i]
        if char == '@':
            i += 1

            tags = IrcMessageTags()
            while True:
                if i == length:
                    raise ValueError()
                if message[i] == ' ':
                    raise ValueError()
                if message[i] == ';':
                    raise ValueError()

                v = []
                isVendor = False
                isKey = False
                value = True
                s = []
                while i < length:
                    char = message[i]
                    i += 1

                    if char == ' ':
                        while i < length and message[i] == ' ':
                            i += 1
                        break
                    elif char == ';':
                        break
                    elif char == '=':
                        break
                    elif char == '.':
                        if len(s) == 0:
                            raise ValueError()
                        if s[-1] == '-':
                            raise ValueError()
                        if not s[0].isalpha():
                            raise ValueError()
                        if not isVendor and v:
                            raise ValueError()
                        v.extend(s)
                        v.append(char)
                        s = []
                        isVendor = True
                    elif char == '/':
                        if isKey:
                            raise ValueError()
                        if len(s) == 0:
                            raise ValueError()
                        if s[-1] == '-':
                            raise ValueError()
                        if not s[0].isalpha():
                            raise ValueError()
                        v.extend(s)
                        s = []
                        isVendor = False
                        isKey = True
                    else:
                        if not char.isalnum() and char != '-' and char != '_':
                            raise ValueError()
                        s.append(char)

                if isVendor:
                    raise ValueError()

                key = ''.join(s)
                vendor = ''.join(v) if v else None

                if char == '=':
                    v = []
                    while i < length:
                        char = message[i]
                        i += 1

                        if char == ' ':
                            while i < length and message[i] == ' ':
                                i += 1
                            break
                        elif char == ';':
                            break
                        if char in '\0\r\n; ':
                            raise ValueError()
                        if char == '\\':
                            if i < length and message[i] in unescapedValue:
                                char = unescapedValue[message[i]]
                                v.append(char)
                                i += 1
                            else:
                                raise ValueError()
                        else:
                            v.append(char)
                    value = ''.join(v)

                tagkey = IrcMessageTagsKey(key, vendor)

                if tagkey in tags:
                    raise ValueError()

                tags[tagkey] = value

                if i == length:
                    raise ValueError()
                if char == ' ':
                    char = message[i]
                    break

        # Prefix
        u: List[str]
        h: List[str]
        s: List[str]
        servername: Optional[str]
        nick: Optional[str]
        user: Optional[str]
        host: Optional[str]
        isServerName: bool
        isNick: bool
        ss: str
        if char == ':':
            i += 1

            if i == length:
                raise ValueError()

            s = []
            servername = None
            nick = None
            user = None
            host = None
            isServerName = False
            isNick = False
            while i < length:
                char = message[i]
                i += 1

                if char == ' ':
                    while i < length and message[i] == ' ':
                        i += 1
                    break
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
                        if s[-1] == '-':
                            raise ValueError()
                        if s[-1] == '.':
                            raise ValueError()
                        s.append(char)
                        isServerName = True
                    else:
                        raise ValueError()
            if isServerName and isNick:
                raise ValueError()
            if len(s) == 0:
                raise ValueError()
            ss = ''.join(s)
            if isServerName:
                if s[-1] == '-':
                    raise ValueError()
                if s[-1] == '.':
                    raise ValueError()
                servername = ss
            else:
                nick = ss

            if char == '!':
                u = []
                while i < length:
                    char = message[i]
                    i += 1

                    if char == ' ':
                        while i < length and message[i] == ' ':
                            i += 1
                        break
                    if char == '.':
                        raise ValueError()
                    if char == '@':
                        break
                    if char in ' \0\r\n':
                        raise ValueError()
                    u.append(char)
                user = ''.join(u)

            if char == '@':
                h = []
                s = []
                while i < length:
                    char = message[i]
                    i += 1

                    if char == ' ':
                        if len(s) == 0:
                            raise ValueError()
                        if s[-1] == '-':
                            raise ValueError()
                        if not s[0].isalpha() and not s[0].isdigit():
                            raise ValueError()
                        h.extend(s)
                        s = []

                        while i < length and message[i] == ' ':
                            i += 1
                        break
                    elif char == '.':
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
                host = ''.join(h)

            prefix = IrcMessagePrefix(servername, nick, user, host)

        # Command
        if i == length:
            raise ValueError()

        s: List[str] = []
        while i < length:
            char = message[i]
            i += 1

            if char == ' ':
                while i < length and message[i] == ' ':
                    i += 1
                break
            if len(s):
                if s[0].isalpha() and not char.isalpha():
                    raise ValueError()
                elif s[0].isdigit() and not char.isdigit():
                    raise ValueError()
            else:
                if not char.isalpha() and not char.isdigit():
                    raise ValueError()
            s.append(char)
        if not s:
            raise ValueError()
        if s[0].isdigit():
            if len(s) != 3:
                raise ValueError()
            command = int(''.join(s))
        else:
            command = ''.join(s)

        # Params
        s: List[str]
        m: List[str]
        t: List[str]
        hasTrailing: bool
        middle: Optional[str] = None
        trailing: Optional[str] = None
        if i != length:
            hasTrailing = False
            s = []
            m = []
            t = []
            while i < length:
                char = message[i]
                i += 1

                if char == ' ':
                    while i < length and message[i] == ' ':
                        i += 1
                    m.extend(s)
                    m.append(' ')
                    s = []
                    continue
                elif char == ':' and not len(s):
                    break
                else:
                    s.append(char)

            if len(s):
                m.extend(s)
            elif len(m):
                del m[-1]

            if char == ':':
                hasTrailing = True
                while i < length:
                    char = message[i]
                    i += 1

                    t.append(char)

            middle = ''.join(m) if m else None
            trailing = ''.join(t) if hasTrailing else None
        params = IrcMessageParams(middle, trailing)

        return ParsedMessage(tags, prefix, command, params)
