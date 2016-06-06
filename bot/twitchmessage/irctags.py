from collections import namedtuple
import collections.abc

ParsedKeyVendor = namedtuple('ParsedKey', ['key', 'vendor'])

escapedValue = {
    ';': '\:',
    ' ': '\\s',
    '\\': '\\\\',
    '\r': '\\r',
    '\n': '\\n'
    }
unescapedValue = {
    ':': ';',
    's': ' ',
    '\\': '\\',
    'r': '\r',
    'n': '\n'
    }

class IrcMessageTagsKey(collections.abc.Hashable):
    __slots__ = ('_vendor', '_key')
    
    def __init__(self, key='', vendor=None):
        if not isinstance(key, str):
            raise TypeError()
        if not isinstance(vendor, (type(None), str)):
            raise TypeError()
        self._key = key
        self._vendor = vendor
    
    @classmethod
    def fromKeyVendor(cls, keyVendor):
        if not isinstance(keyVendor, str):
            raise TypeError()
        return cls(*cls.parse(keyVendor))
    
    def __str__(self):
        s = self._key
        if self._vendor is not None:
            s = self._vendor + '/' + s
        return s
    
    def __eq__(self, other):
        if isinstance(other, IrcMessageTagsKey):
            return self._key == other._key and self._vendor == other._vendor
        if isinstance(other, str):
            return str(self) == other
        return False
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return str(self).__hash__()
    
    @staticmethod
    def parse(keyToParse):
        if not isinstance(keyToParse, str):
            raise ValueError()
        
        length = len(keyToParse)
        i = 0
        
        if i == length:
            raise ValueError()
        
        v = []
        key = ''
        isVendor = False
        s = []
        while i < length:
            char = keyToParse[i]
            i += 1
                    
            if char == '.':
                if len(s) == 0:
                    raise ValueError()
                if s[-1] == '-':
                    raise ValueError()
                if not s[0].isalpha():
                    raise ValueError()
                if not isVendor and vendor:
                    raise ValueError()
                s.append(char)
                vendor.append(''.join(s))
                s = []
                isVendor = True
            elif char == '/':
                if len(s) == 0:
                    raise ValueError()
                if s[-1] == '-':
                    raise ValueError()
                if not s[0].isalpha():
                    raise ValueError()
                vendor.append(''.join(s))
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
        
        key = ''.join(s)
        vendor = ''.join(v) if v else None
        return ParsedKeyVendor(key, vendor)

class IrcMessageTagsReadOnly(collections.abc.Mapping):
    __slots__ = ('_items')
    
    def __new__(cls, items=None):
        # This returns itself, only for read only
        if cls is type(items) and cls is IrcMessageTagsReadOnly:
            return items
        return super().__new__(cls)
    
    def __init__(self, items=None):
        # This returns itself, only for read only
        if self is items:
            return
        
        self._items = {}
        if items is not None:
            if isinstance(items, str):
                self._items = parseTags(items)
            elif isinstance(items, collections.abc.Mapping):
                for key in items:
                    if (items[key] is not True
                            and not isinstance(items[key], str)):
                        raise TypeError()
                    self._items[self.__class__.fromKey(key)] = items[key]
            elif isinstance(items, collections.abc.Iterable):
                for key in items:
                    if (isinstance(key, collections.abc.Sequence)
                            and len(key) >= 2):
                        if (items[key[1]] is not True
                                and not isinstance(items[key[1]], str)):
                            raise TypeError()
                        self._items[self.__class__.fromKey(key[0])] = key[1]
                    else:
                        self._items[self.__class__.fromKey(key)] = True
            else:
                raise TypeError()

    @staticmethod
    def fromKey(key):
        if isinstance(key, IrcMessageTagsKey):
            return key
        else:
            return IrcMessageTagsKey.fromKeyVendor(key)
    
    def __getitem__(self, key):
        if not isinstance(key, IrcMessageTagsKey):
            key = IrcMessageTagsKey.fromKeyVendor(key)
        return self._items[key]
    
    def __iter__(self):
        for i in self._items:
            yield i
    
    def __len__(self):
        return len(self._items)
    
    def __str__(self):
        s = []
        for k in self._items:
            if self._items[k] is True:
                s.append(str(k))
            else:
                s.append(str(k) + '='
                         + self.__class__.formatValue(self._items[k]))
        return ';'.join(s)
    
    @staticmethod
    def formatValue(value):
        if not isinstance(value, str):
            raise ValueError
        
        s = []
        
        for char in value:
            if char in escapedValue:
                char = escapedValue[char]
            s.append(char)
        return ''.join(s)
    
    @staticmethod
    def parseTags(tags):
        if not isinstance(tags, str):
            raise TypeError()
        
        length = len(tags)
        i = 0
        
        if i == length:
            raise ValueError()
        
        items = {}
        while True:
            if tags[i] == ';':
                raise ValueError()
            
            v = []
            key = ''
            isVendor = False
            isKey = False
            value = True
            s = []
            while i < length:
                char = tags[i]
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
            
            key = ''.join(s)
            vendor = ''.join(v) if v else None
            
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
            
            tagkey = IrcMessageTagsKey(key, vendor)
            
            if tagkey in items:
                raise ValueError()
            
            items[tagkey] = value
            
            if i == length:
                break
        
        return items

class IrcMessageTags(IrcMessageTagsReadOnly, collections.abc.MutableMapping):
    __slots__ = ('_items')
    
    def __setitem__(self, key, value):
        if isinstance(key, str):
            key = IrcMessageTagsKey.fromKeyVendor(key)
        elif isinstance(key, IrcMessageTagsKey):
            pass
        else:
            raise TypeError()
        if value is True:
            self._items[key] = value
        elif isinstance(value, str):
            self._items[key] = value
        else:
            raise ValueError()
    
    def __delitem__(self, key):
        del self._items[key]
