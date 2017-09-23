from typing import List


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
