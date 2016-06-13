from typing import Any, Dict, Hashable, Iterable, Iterator, List, Mapping
from typing import MutableMapping, NamedTuple, Optional, Sequence, Tuple, Union

KeyParam = Union['IrcMessageTagsKey', str]
TagValue = Union[bool, str]

ParsedKeyVendor = NamedTuple('ParsedKey',
                             [('key', str), ('vendor', Optional[str])])

escapedValue = {
    ';': '\:',
    ' ': '\\s',
    '\\': '\\\\',
    '\r': '\\r',
    '\n': '\\n'
    }  # type: Dict[str, str]
unescapedValue = {
    ':': ';',
    's': ' ',
    '\\': '\\',
    'r': '\r',
    'n': '\n'
    }  # type: Dict[str, str]


class IrcMessageTagsKey(Hashable):
    __slots__ = ('_vendor', '_key')
    
    def __init__(self,
                 key:str='',
                 vendor:Optional[str]=None) -> None:
        if not isinstance(key, str):
            raise TypeError()
        if not isinstance(vendor, (type(None), str)):
            raise TypeError()
        self._key = key  # type: str
        self._vendor = vendor  # type: Optional[str]
    
    @classmethod
    def fromKeyVendor(cls, keyVendor:str) -> 'IrcMessageTagsKey':
        if not isinstance(keyVendor, str):
            raise TypeError()
        return cls(*cls.parse(keyVendor))

    @property
    def key(self) -> str:
        return self._key

    @property
    def vendor(self) -> Optional[str]:
        return self._vendor
    
    def __str__(self) -> str:
        s = self._key
        if self._vendor is not None:
            s = self._vendor + '/' + s
        return s
    
    def __eq__(self, other:object) -> bool:
        if isinstance(other, IrcMessageTagsKey):
            return self._key == other._key and self._vendor == other._vendor
        if isinstance(other, str):
            return str(self) == other
        return False
    
    def __ne__(self, other:object) -> bool:
        return not self.__eq__(other)
    
    def __hash__(self) -> int:
        return str(self).__hash__()
    
    @staticmethod
    def parse(keyToParse:str) -> ParsedKeyVendor:
        if not isinstance(keyToParse, str):
            raise ValueError()
        
        length = len(keyToParse)  # type: int
        i = 0  # type: int
        
        if i == length:
            return ParsedKeyVendor('', None)
        
        v = []  # type: List[str]
        isVendor = False  # type: bool
        s = []  # type: List[str]
        while i < length:
            char = keyToParse[i]  # type: str
            i += 1
                    
            if char == '.':
                if len(s) == 0:
                    raise ValueError()
                if s[-1] == '-':
                    raise ValueError()
                if not s[0].isalpha():
                    raise ValueError()
                if not isVendor and v:
                    raise ValueError()
                s.append(char)
                v.append(''.join(s))
                s = []
                isVendor = True
            elif char == '/':
                if len(s) == 0:
                    raise ValueError()
                if s[-1] == '-':
                    raise ValueError()
                if not s[0].isalpha():
                    raise ValueError()
                v.append(''.join(s))
                s = []
                isVendor = False
            else:
                if not char.isalnum() and char != '-' and char != '_':
                    raise ValueError()
                s.append(char)
            
        if i != length:
            raise ValueError()
        if isVendor:
            raise ValueError()
        
        key = ''.join(s)  # type: str
        vendor = ''.join(v) if v else None  # type: Optional[str]
        return ParsedKeyVendor(key, vendor)


class IrcMessageTagsReadOnly(Mapping[IrcMessageTagsKey, TagValue]):
    __slots__ = '_items',
    
    def __new__(cls, items:Any=None) -> Any:
        # This returns itself, only for read only
        if cls is type(items) and cls is IrcMessageTagsReadOnly:
            return items
        return super().__new__(cls)
    
    def __init__(self, items:Any=None) -> None:
        # This returns itself, only for read only
        if self is items:
            return
        
        self._items = {}  # type: Dict[IrcMessageTagsKey, TagValue]
        if items is not None:
            if isinstance(items, str):
                self._items = self.parseTags(items)
            elif isinstance(items, Mapping):
                for key in items:
                    if (items[key] is not True
                            and not isinstance(items[key], str)):
                        raise TypeError()
                    self._items[self.fromKey(key)] = items[key]
            elif isinstance(items, Iterable[Union[IrcMessageTagsKey, str,
                                                  Tuple[KeyParam, str]]]):
                for key in items: # --type: Union[IrcMessageTagsKey, str, Tuple[KeyParam, str]]
                    if (isinstance(key, Sequence)
                            and len(key) >= 2):
                        if (key[1] is not True
                                and not isinstance(key[1], str)):
                            raise TypeError()
                        self._items[self.fromKey(key[0])] = key[1]
                    else:
                        self._items[self.fromKey(key)] = True
            else:
                raise TypeError()

    @staticmethod
    def fromKey(key:KeyParam) -> IrcMessageTagsKey:
        if isinstance(key, IrcMessageTagsKey):
            return key
        else:
            return IrcMessageTagsKey.fromKeyVendor(key)
    
    def __getitem__(self, key:KeyParam) -> TagValue:
        if not isinstance(key, IrcMessageTagsKey):
            key = IrcMessageTagsKey.fromKeyVendor(key)
        return self._items[key]
    
    def __iter__(self) -> Iterator[IrcMessageTagsKey]:
        for i in self._items:  # --type: IrcMessageTagsKey
            yield i
    
    def __len__(self) -> int:
        return len(self._items)
    
    def __str__(self) -> str:
        s = []  # type: List[str]
        for k in self._items:
            if self._items[k] is True:
                s.append(str(k))
            else:
                s.append(str(k) + '='
                         + self.formatValue(self._items[k]))
        return ';'.join(s)
    
    @staticmethod
    def formatValue(value) -> str:
        if not isinstance(value, str):
            raise ValueError
        
        s = []  # type: List[str]
        
        for char in value:
            if char in escapedValue:
                char = escapedValue[char]
            s.append(char)
        return ''.join(s)
    
    @staticmethod
    def parseTags(tags:str) -> Dict[IrcMessageTagsKey, TagValue]:
        if not isinstance(tags, str):
            raise TypeError()
        
        length = len(tags)  # type: int
        i = 0  # type: int
        
        if i == length:
            raise ValueError()
        
        items = {}  # type: Dict[IrcMessageTagsKey, TagValue]
        while True:
            if tags[i] == ';':
                raise ValueError()
            
            v = []  # type: List[str]
            isVendor = False  # type: bool
            isKey = False  # type: bool
            value = True  # type: TagValue
            s = []  # type: List[str]
            while i < length:
                char = tags[i]  # type: str
                i += 1
                
                if char == ';':
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
            
            key = ''.join(s)  # type: str
            vendor = ''.join(v) if v else None  # type: Optional[str]
            
            if char == '=':
                v = []
                while i < length:
                    char = tags[i]
                    i += 1
                
                    if char == ';':
                        break
                    if char in '\0\r\n; ':
                        raise ValueError()
                    if char == '\\':
                        if i < length and tags[i] in unescapedValue:
                            char = unescapedValue[tags[i]]
                            v.append(char)
                            i += 1
                        else:
                            raise ValueError()
                    else:
                        v.append(char)
                value = ''.join(v)
            
            tagkey = IrcMessageTagsKey(key, vendor)  # type: IrcMessageTagsKey
            
            if tagkey in items:
                raise ValueError()
            
            items[tagkey] = value
            
            if i == length:
                break
        
        return items


class IrcMessageTags(IrcMessageTagsReadOnly,
                     MutableMapping[IrcMessageTagsKey, TagValue]):
    __slots__ = '_items',
        
    def __setitem__(self,
                    key:KeyParam,
                    value:TagValue) -> None:
        if isinstance(key, str):
            key = IrcMessageTagsKey.fromKeyVendor(key)
        elif not isinstance(key, IrcMessageTagsKey):
            raise TypeError()
        if value is True:
            self._items[key] = value
        elif isinstance(value, str):
            self._items[key] = value
        else:
            raise ValueError()
    
    def __delitem__(self, key:KeyParam):
        if isinstance(key, str):
            key = IrcMessageTagsKey.fromKeyVendor(key)
        elif not isinstance(key, IrcMessageTagsKey):
            raise TypeError()
        del self._items[key]
