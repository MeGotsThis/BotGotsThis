from source.data import ChatCommand
from typing import Iterable, Mapping, Optional


def disableFilters() -> bool:
    return True


def disableCustomMessage() -> bool:
    return True


def filterMessage() -> Iterable[ChatCommand]:
    return []


def commands() -> Mapping[str, Optional[ChatCommand]]:
    if not hasattr(commands, 'commands'):
        setattr(commands, 'commands', {
            '!exit': None,
            '!managebot': None,
            '!reload': None,
            '!reloadcommands': None,
            '!reloadconfig': None,
            '!join': None,
            '!part': None,
            '!emptychat': None,
            '!emptyall': None,
            '!global': None,
            '!say': None,
            '!hello': None,
            '!leave': None,
            '!feature': None,
            '!empty': None,
            '!autorepeat': None,
            '!pyramid': None,
            '!rpyramid': None,
            '!wall': None,
            '!status': None,
            '!title': None,
            '!game': None,
            '!setgame': None,
            '!purge': None,
            '!rekt': None,
            '!command': None,
            '!full': None,
            '!parenthesized': None,
            '!circled': None,
            '!smallcaps': None,
            '!upsidedown': None,
            '!come': None,
            '!autojoin': None,
            '!uptime': None,
            })
    return getattr(commands, 'commands')


def commandsStartWith() -> Mapping[str, Optional[ChatCommand]]:
    if not hasattr(commandsStartWith, 'commands'):
        setattr(commandsStartWith, 'commands', {
            '!pyramid-': None,
            '!wall-': None,
            '!autorepeat-': None,
            })
    return getattr(commandsStartWith, 'commands')


def noCommand() -> Iterable[ChatCommand]:
    return []
