from enum import Enum
from typing import List, Set  # noqa: F401


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
    if argument in yes:
        return Yes
    if argument in no:
        return No
    return Unknown
