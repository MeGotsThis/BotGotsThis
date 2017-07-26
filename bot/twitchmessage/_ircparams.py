from typing import List, NamedTuple, Optional  # noqa: F401


class ParsedParams(NamedTuple):
    middle: Optional[str]
    trailing: Optional[str]


class IrcMessageParams:
    __slots__ = ('_middle', '_trailing')

    def __init__(self,
                 middle: Optional[str]=None,
                 trailing: Optional[str]=None) -> None:
        if not isinstance(middle, (type(None), str)):
            raise TypeError(f'middle: {type(middle).__name__}')
        if not isinstance(trailing, (type(None), str)):
            raise TypeError(f'trailing: {type(trailing).__name__}')

        if middle is not None:
            if not middle:
                raise ValueError(f'middle is empty')
            if any([s for s in middle.split(' ') if len(s) and s[0] == ':']):
                raise ValueError(f'middle: {middle}')
            if set(middle) == {' '} or any(c in '\0\r\n' for c in middle):
                raise ValueError(f'middle: {middle}')
        if trailing is not None and any(c in '\0\r\n' for c in trailing):
            raise ValueError(f'trailing: {trailing}')

        self._middle: Optional[str] = middle
        self._trailing: Optional[str] = trailing

    @classmethod
    def fromParams(cls, params: str) -> 'IrcMessageParams':
        if not isinstance(params, str):
            raise TypeError()
        return cls(*cls.parse(params))

    @property
    def isEmpty(self) -> bool:
        return self._middle is None and self._trailing is None

    @property
    def middle(self) -> Optional[str]:
        return self._middle

    @property
    def trailing(self) -> Optional[str]:
        return self._trailing

    def __str__(self) -> str:
        s = ''
        if self._middle is not None:
            s += self._middle
        if self._middle is not None and self._trailing is not None:
            s += ' '
        if self._trailing is not None:
            s += ':' + self._trailing
        return s

    def __eq__(self, other: object) -> bool:
        if isinstance(other, IrcMessageParams):
            return (self._middle == other._middle
                    and self._trailing == other._trailing)
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @staticmethod
    def parse(params: str) -> ParsedParams:
        if not isinstance(params, str):
            raise TypeError()

        length: int = len(params)
        i: int = 0

        if i == length:
            return ParsedParams(None, None)

        char: str
        middle: Optional[str]
        trailing: Optional[str]
        hasTrailing: bool = False
        s: List[str] = []
        m: List[str] = []
        t: List[str] = []
        while i < length:
            char = params[i]
            i += 1

            if char == ' ':
                while i < length and params[i] == ' ':
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
                char = params[i]
                i += 1

                t.append(char)

        if i != length:
            raise ValueError()

        middle = ''.join(m) if m else None
        trailing = ''.join(t) if hasTrailing else None

        return ParsedParams(middle, trailing)
