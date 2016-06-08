from typing import List, NamedTuple, Optional

ParsedParams = NamedTuple('ParsedParams',
                          [('middle', Optional[str]),
                           ('trailing', Optional[str])])


class IrcMessageParams:
    __slots__ = ('_middle', '_trailing')
    
    def __init__(self,
                 middle:Optional[str]=None,
                 trailing:Optional[str]=None) -> None:
        if not isinstance(middle, (type(None), str)):
            raise TypeError()
        if not isinstance(trailing, (type(None), str)):
            raise TypeError()

        if middle is not None:
            if any([s for s in middle.split(' ') if len(s) and s[0] == ':']):
                raise ValueError()

        self._middle = middle  # type: Optional[str]
        self._trailing = trailing  # type: Optional[str]

    @classmethod
    def fromParams(cls, params:str) -> 'IrcMessageParams':
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

    def __eq__(self, other:object) -> bool:
        if isinstance(other, IrcMessageParams):
            return (self._middle == other._middle
                    and self._trailing == other._trailing)
        return False
    
    def __ne__(self, other:object) -> bool:
        return not self.__eq__(other)
    
    @staticmethod
    def parse(params:str) -> ParsedParams:
        if not isinstance(params, str):
            raise ValueError()
        
        length = len(params)  # type: int
        i = 0  # type: int
        
        if i == length:
            return ParsedParams(None, None)
        
        s = []  # type: List[str]
        m = []  # type: List[str]
        t = []  # type: List[str]
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
            while i < length:
                char = params[i]
                i += 1
                
                t.append(char)
        
        if i != length:
            raise ValueError()
        
        middle = ''.join(m) if m else None  # type: Optional[str]
        trailing = ''.join(t) if t else None  # type: Optional[str]
        
        return ParsedParams(middle, trailing)
