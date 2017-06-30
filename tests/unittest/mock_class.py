import itertools

from datetime import datetime, timedelta


sentinal = object()


class TypeMatch:
    def __init__(self, type):
        self.type = type

    def __eq__(self, other):
        return isinstance(other, self.type)

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return 'TypeMatch(' + repr(self.type) + ')'


class Contains(TypeMatch):
    def __init__(self, type, *matches):
        super().__init__(type)
        self.matches = matches

    def __eq__(self, other):
        if not super().__eq__(other):
            return False
        for m in self.matches:
            if m not in other:
                return False
        return True

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return ('Contains(' + repr(self.type) + ', '
                + ', '.join(repr(m) for m in self.matches) + ')')


class StrContains(Contains):
    def __init__(self, *matches):
        super().__init__(str, *matches)

    def __repr__(self):
        return 'StrContains(' + ', '.join(repr(m) for m in self.matches) + ')'


class IterableMatch:
    def __init__(self, *matches):
        self.matches = matches

    def __eq__(self, other):
        for m, o in itertools.zip_longest(self.matches, other):
            if m != o:
                return False
        return True

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return ('IterableMatch('
                + ', '.join(repr(m) for m in self.matches) + ')')


class PartialMatch:
    def __init__(self, func, *args, **keywords):
        self.func = func
        self.args = args
        self.keywords = keywords

    def __eq__(self, other):
        if hasattr(other, 'func'):
            return (self.func is other.func and self.args == other.args
                    and self.keywords == other.keywords)
        return False

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return ('PartialMatch(' + repr(self.func) + ', '
                + ', '.join(repr(m) for m in self.args)
                + (', ' if self.keywords else '')
                + ', '.join(k + '=' + repr(self.keywords[k]) for k
                            in self.keywords)
                + ')')


class AsyncIterator:
    def __init__(self, seq):
        self.iter = iter(seq)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration


class DateTimeNear:
    def __init__(self, dt, epsilon=timedelta(seconds=1)):
        self.dt = dt
        self.epsilon = epsilon

    def __eq__(self, other):
        if not isinstance(other, datetime):
            return False
        return -self.epsilon <= self.dt - other <= self.epsilon
