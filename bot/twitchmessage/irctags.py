_escapedValue = {
    ';': '\:',
    ' ': '\\s',
    '\\': '\\\\',
    '\r': '\\r',
    '\n': '\\n'
    }
_unescapedValue = {
    ':': ';',
    's': ' ',
    '\\': '\\',
    'r': '\r',
    'n': '\n'
    }

class IrcMessageTags:
    __slots__ = ('_items')
    
    def __init__(self, items=None):
        self._items = {}
        if items is not None:
            validDict = (dict, IrcMessageTags, IrcMessageTagsReadOnly,
                         IrcMessageTags,)
            validList = (list, tuple)
            validSet = (set,)
            if isinstance(items, str):
                self._items = parseTags(items)
            elif isinstance(items, validDict):
                for key in items:
                    if isinstance(key, IrcMessageTagsKey):
                        k = key
                    else:
                        k = IrcMessageTagsKey.fromKeyVendor(key)
                    if items[key] is True or isinstance(items[key], str):
                        self._items[k] = items[key]
                    else:
                        raise TypeError()
            elif isinstance(items, validList):
                for key in items:
                    if isinstance(key, validList) and len(key) >= 2:
                        k = IrcMessageTagsKey.parse(key[0])
                        self._items[k] = key[1]
                    else:
                        k = IrcMessageTagsKey.parse(key)
                        self._items[k] = True
            elif isinstance(items, validSet):
                for key in items:
                    k = IrcMessageTagsKey.parse(key)
                    self._items[k] = True
   
    def __len__(self):
        return len(self._items)
    
    def __getitem__(self, key):
        if isinstance(key, str):
            key = IrcMessageTagsKey.fromKeyVendor(key)
        elif isinstance(key, IrcMessageTagsKey):
            pass
        else:
            raise TypeError()
        return self._items[key]
    
    def __setitem__(self, key, value):
        if isinstance(key, str):
            key = IrcMessageTagsKey.fromKeyVendor(key)
        elif isinstance(key, IrcMessageTagsKey):
            pass
        else:
            raise TypeError()
        if value == True:
            self._items[key] = value
        elif isinstance(value, str):
            self._items[key] = value
        else:
            raise ValueError()
    
    def __delitem__(self, key):
        del self._items[key]
    
    def __contains__(self, item):
        if isinstance(item, str):
            item = IrcMessageTagsKey.fromKeyVendor(item)
        elif isinstance(item, IrcMessageTagsKey):
            pass
        else:
            raise TypeError()
        return item in self._items
    
    def __iter__(self):
        for i in self._items:
            yield i
    
    def __str__(self):
        s = []
        for k in self._items:
            if self._items[k] is True:
                s.append(str(k))
            else:
                s.append(str(k) + '=' + formatValue(self._items[k]))
        return ';'.join(s)
    
    def __eq__(self, other):
        if isinstance(other, (IrcMessageTags, IrcMessageTagsReadOnly)):
            return self._items == other._items
        return False
    
    def __ne__(self, other):
        return not self.__eq__(other)

class IrcMessageTagsReadOnly:
    __slots__ = ('_items')
    
    def __init__(self, *, items=None):
        self._items = {}
        if items is not None:
            validDict = (dict, IrcMessageTags, IrcMessageTagsReadOnly,
                         IrcMessageTags,)
            validList = (list, tuple)
            validSet = (set,)
            if isinstance(items, str):
                self._items = parseTags(items)
            elif isinstance(items, validDict):
                for key in items:
                    if isinstance(key, IrcMessageTagsKey):
                        k = key
                    else:
                        k = IrcMessageTagsKey.fromKeyVendor(key)
                    self._items[k] = items[key]
            elif isinstance(items, validList):
                for key in items:
                    if isinstance(k, validList) and len(k) >= 2:
                        k = IrcMessageTagsKey.parse(k[0])
                        self._items[k] = key[1]
                    else:
                        k = IrcMessageTagsKey.parse(key)
                        self._items[k] = True
            elif isinstance(items, validSet):
                for key in items:
                    k = IrcMessageTagsKey.parse(key)
                    self._items[k] = True
   
    def __len__(self):
        return len(self._items)
    
    def __getitem__(self, key):
        if isinstance(key, str):
            key = IrcMessageTagsKey.fromKeyVendor(key)
        elif isinstance(key, IrcMessageTagsKey):
            pass
        else:
            raise TypeError()
        return self._items[key]
    
    def __contains__(self, item):
        if isinstance(item, str):
            item = IrcMessageTagsKey.fromKeyVendor(key)
        elif isinstance(item, IrcMessageTagsKey):
            pass
        else:
            raise TypeError()
        return item in self._items
    
    def __iter__(self):
        for i in self._items:
            yield i
    
    def __str__(self):
        s = []
        for k in self._items:
            if self._items[k] is True:
                s.append(str(k))
            else:
                s.append(str(k) + '=' + formatValue(self._items[k]))
        return ';'.join(s)
    
    def __eq__(self, other):
        if isinstance(other, (IrcMessageTags, IrcMessageTagsReadOnly)):
            return self._items == other._items
        return False
    
    def __ne__(self, other):
        return not self.__eq__(other)

class IrcMessageTagsKey:
    __slots__ = ('_vendor', '_key')
    
    def __init__(self, key='', vendor=None):
        if isinstance(key, str):
            pass
        else:
            raise TypeError()
        if vendor is None or isinstance(vendor, str):
            pass
        else:
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
        if isinstance(keyToParse, IrcMessageTagsKey):
            return keyToParse
        if isinstance(keyToParse, str):
            pass
        else:
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
        return (key, vendor)

def formatValue(value):
    if isinstance(value, str):
        pass
    else:
        raise ValueError
    
    s = []
        
    for char in value:
        if char in _escapedValue:
            char = _escapedValue[char]
        s.append(char)
    return ''.join(s)

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
                    if (i < length and
                        tags[i] in _unescapedValue):
                        char = _unescapedValue[tags[i]]
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
