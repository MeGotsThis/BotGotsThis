from . import ircparams
from . import ircprefix
from . import irctags
import string

class IrcMessage:
    __slots__ = ('_tags', '_prefix', '_command', '_params')
    
    def __init__(self, *, message=None, tags=None, prefix=None, command=0,
                 params=ircparams.IrcMessageParams()):
        if isinstance(message, str):
            tags, prefix, command, params = IrcMessage._parse(message)
        if tags is None or isinstance(tags, irctags.IrcMessageTagsReadOnly):
            pass
        elif isinstance(tags, irctags.IrcMessageTags):
            tags = irctags.IrcMessageTagsReadOnly(items=tags)
        else:
            raise TypeError()
        if prefix is None or isinstance(prefix, ircprefix.IrcMessagePrefix):
            pass
        else:
            raise TypeError()
        if isinstance(command, str):
            if not command.isalpha():
                raise ValueError()
        elif isinstance(command, int):
            if not (0 <= command <= 999):
                raise ValueError()
        else:
            raise TypeError()
        if isinstance(params, ircparams.IrcMessageParams):
            pass
        else:
            raise TypeError()
        
        self._tags = tags
        self._prefix = prefix
        self._command = command
        self._params = params
    
    @property
    def tags(self):
        return self._tags
    
    @property
    def prefix(self):
        return self._prefix
    
    @property
    def command(self):
        return self._command
    
    @property
    def params(self):
        return self._params
    
    def __str__(self):
        message = ''
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
    
    def __eq__(self, other):
        if isinstance(other, IrcMessage):
            return (self._tags == other._tags and
                    self._prefix == other._prefix and
                    self._command == other._command and
                    self._params == other._params)
        return False
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    @staticmethod
    def _parse(message):
        if isinstance(message, str):
            pass
        else:
            raise ValueError()
        
        length = len(message)
        i = 0
        
        if i == length:
            raise ValueError()
        
        # Tags
        tags = None
        char = message[i]
        if char == '@':
            i += 1
            
            if i == length:
                raise ValueError()
            
            tags = irctags.IrcMessageTags()
            while True:
                if message[i] == ' ':
                    raise ValueError()
                if message[i] == ';':
                    raise ValueError()
                
                v = []
                key = ''
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
                            if (i < length and
                                message[i] in irctags._unescapedValue):
                                char = irctags._unescapedValue[message[i]]
                                v.append(char)
                                i += 1
                            else:
                                raise ValueError()
                        else:
                            v.append(char)
                    value = ''.join(v)
                
                tagkey = irctags.IrcMessageTagsKey(key=key, vendor=vendor)
                
                if tagkey in tags:
                    raise ValueError()
                
                tags[tagkey] = value
                
                if char == ' ':
                    char = message[i]
                    break
        
        # Prefix
        prefix = None
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
                    if (char in string.ascii_letters or char.isdigit() or
                        char == '-'):
                        s.append(char)
                    elif char in ircprefix._nickSpecials:
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
            
            prefix = ircprefix.IrcMessagePrefix(servername=servername,
                                                nick=nick,
                                                user=user,
                                                host=host)
        
        # Command
        if i == length:
            raise ValueError()
        
        s = []
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
        if s[0].isdigit():
            if len(s) != 3:
                raise ValueError()
            command = int(''.join(s))
        else:
            command = ''.join(s)
        
        # Params
        middle = None
        trailing = None
        if i != length:
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
                while i < length:
                    char = message[i]
                    i += 1
                    
                    t.append(char)
            
            middle = ''.join(m) if m else None
            trailing = ''.join(t) if t else None
        params = ircparams.IrcMessageParams(middle=middle, trailing=trailing)
        
        return (tags, prefix, command, params)
