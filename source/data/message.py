class Tokenized:
    def __init__(self, string):
        if not isinstance(string, str):
            raise TypeError('message needs to be a str')
        self._string = string
        self._tokens = self._string.split()
        self._command = None
    
    def __str__(self):
        return self._string
    
    def __len__(self):
        return len(self._tokens)
    
    def __getitem__(self, key):
        if isinstance(key, int):
            return self._tokens[key]
        if isinstance(key, slice):
            if key.start is not None and not isinstance(key.start, int):
                raise ValueError('start is not of type int')
            if key.stop is not None and not isinstance(key.stop, int):
                raise ValueError('stop is not of type int')
            if key.step is not None:
                if not isinstance(key.step, int):
                    raise ValueError('step is not of type int')
                if key.step != 1:
                    raise ValueError('step other than 1 is not supported')
            lenTokens = len(self._tokens)
            
            # Trivial cases
            if not self._string:
                return self._string
            if key.start is not None:
                if key.start >= lenTokens:
                    return ''
            if key.stop is not None:
                if key.stop == 0 or -key.stop >= lenTokens:
                    return ''
            
            message = self._string
            start = 0
            if key.start is not None:
                if key.start == 0:
                    pass
                elif key.start >= lenTokens:
                    return ''
                elif key.start > 0:
                    start = key.start
                    message = message.split(None, key.start)[-1]
                elif -key.start < lenTokens:
                    start = key.start + lenTokens
                    message = message.split(None, key.start + lenTokens)[-1]
            if key.stop is not None:
                stop = key.stop - start
                if 0 < key.stop < lenTokens:
                    message = message.rsplit(None, lenTokens - start - stop)[0]
                elif 0 < -key.stop < lenTokens:
                    message = message.rsplit(None, -stop - start)[0]
            return message
        raise TypeError('key is not of type int or slice')
    
    def __iter__(self):
        yield from self._tokens
    
    def __reversed__(self):
        yield from self._tokens.reverse()
    
    def __contains__(self, item):
        return item in self._tokens


class Message(Tokenized):
    def __init__(self, message):
        super().__init__(message)
        self._query = None
        self._lower = None
    
    @property
    def command(self):
        return self.lower[0]
    
    @property
    def query(self):
        if self._query is None:
            self._query = self[1:]
        return self._query
    
    @property
    def lower(self):
        if self._lower is None:
            self._lower = Tokenized(self._string.lower())
        return self._lower
