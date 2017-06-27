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
            '!community': None,
            '!purge': None,
            '!permit': None,
            '!command': None,
            '!full': None,
            '!parenthesized': None,
            '!circled': None,
            '!smallcaps': None,
            '!upsidedown': None,
            '!serifbold': None,
            '!serif-bold': None,
            '!serifitalic': None,
            '!serif-italic': None,
            '!serifbolditalic': None,
            '!serif-bolditalic': None,
            '!serifbold-italic': None,
            '!serif-bold-italic': None,
            '!serifitalicbold': None,
            '!serif-italicbold': None,
            '!serifitalic-bold': None,
            '!serif-italic-bold': None,
            '!sanserif': None,
            '!sanserifbold': None,
            '!sanserif-bold': None,
            '!bold': None,
            '!sanserifitalic': None,
            '!sanserif-italic': None,
            '!italic': None,
            '!sanserifbolditalic': None,
            '!sanserif-bolditalic': None,
            '!sanserifbold-italic': None,
            '!sanserif-bold-italic': None,
            '!bolditalic': None,
            '!bold-italic': None,
            '!sanserifitalicbold': None,
            '!sanserif-italicbold': None,
            '!sanserifitalic-bold': None,
            '!sanserif-italic-bold': None,
            '!italicbold': None,
            '!italic-bold': None,
            '!script': None,
            '!cursive': None,
            '!scriptbold': None,
            '!cursivebold': None,
            '!script-bold': None,
            '!cursive-bold': None,
            '!fraktur': None,
            '!frakturbold': None,
            '!fraktur-bold': None,
            '!monospace': None,
            '!doublestruck': None,
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
            '!settimeoutlevel-': None,
            })
    return getattr(commandsStartWith, 'commands')


def noCommand() -> Iterable[ChatCommand]:
    return []
