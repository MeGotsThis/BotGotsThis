from enum import Enum
from typing import List, Set  # noqa: F401

twitchUrlRegex: str = (
    # r"(?:game:(?:[-a-zA-Z0-9@:%_\+.~#?&//=]*))|"
    r"(?:https?:\/\/)?(?:[-a-zA-Z0-9@:%_\+~#=]+\.)+[a-z]{2,6}\b"
    r"(?:[-a-zA-Z0-9@:%_\+.~#?&//=]*)")


class Response(Enum):
    No = False
    Yes = True
    Unknown = None


Yes = Response.Yes
No = Response.No
Unknown = Response.Unknown


def parseArguments(arguments: str) -> List[str]:
    argumentList: List[str] = []
    subWord: List[str] = []
    inQuote = False
    i: int = 0
    length: int = len(arguments)
    while i < length:
        c: str = arguments[i]
        i += 1
        if c == '\\':
            if i < length and arguments[i] in '"\\ ':
                subWord.append(arguments[i])
                i += 1
                continue
        if c == ' ' and not inQuote:
            argumentList.append(''.join(subWord))
            subWord.clear()
            continue
        if c == '"':
            inQuote = not inQuote
            continue
        subWord.append(c)
    if subWord:
        argumentList.append(''.join(subWord))
    return argumentList


def get_response(argument: str, default: Response=Unknown) -> Response:
    yes: Set[str] = {
        'yes',
        'y',
        'true',
        't',
        'enable',
        'e',
        'on',
        '1',
    }
    no: Set[str] = {
        'no',
        'n',
        'false',
        'f',
        'disable',
        'd',
        'off',
        '0',
    }

    if not argument:
        return default
    lower: str = argument.lower()
    if lower in yes:
        return Yes
    if lower in no:
        return No
    return Unknown
