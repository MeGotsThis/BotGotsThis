class IrcMessageParams:
    __slots__ = ('_middle', '_trailing')
    
    def __init__(self, *, params=None, middle=None, trailing=None):
        if isinstance(params, str):
            middle, trailing = IrcMessageParams._parse(params)
        
        if middle is None or isinstance(middle, str):
            pass
        else:
            raise TypeError()
        if trailing is None or isinstance(trailing, str):
            pass
        else:
            raise TypeError()
        
        if middle is not None:
            if any([s for s in middle.split(' ') if len(s) and s[0] == ':']):
                raise ValueError()
        
        self._middle = middle
        self._trailing = trailing
    
    @property
    def isEmpty(self):
        return self._middle is None and self._trailing is None
    
    @property
    def middle(self):
        return self._middle
    
    @property
    def trailing(self):
        return self._trailing
    
    def __str__(self):
        s = ''
        if self._middle is not None:
            s += self._middle
        if self._middle is not None and self._trailing is not None:
            s += ' '
        if self._trailing is not None:
            s += ':' + self._trailing
        return s
    
    def __eq__(self, other):
        if isinstance(other, IrcMessageParams):
            return (self._middle == other._middle and
                    self._trailing == other._trailing)
        return False
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    @staticmethod
    def _parse(params):
        if isinstance(params, str):
            pass
        else:
            raise ValueError()
        
        length = len(params)
        i = 0
        
        if i == length:
            return (None, None)
        
        s = []
        m = []
        t = []
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
        
        middle = ''.join(m) if m else None
        trailing = ''.join(t) if t else None
        
        return (servername, nick, user, host)
