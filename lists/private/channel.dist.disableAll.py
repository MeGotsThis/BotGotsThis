from source.data.argument import ChatCommandArgs
from typing import Callable, List, Mapping, Optional

disableFilters = True  # type: bool
disableCustomMessage = True  # type: bool

filterMessage = []  # type: List[Callable[[ChatCommandArgs], bool]]
commands = {
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
    }  # type: Mapping[str, Optional[Callable[[ChatCommandArgs], bool]]]
commandsStartWith = {
    '!pyramid-': None,
    '!wall-': None,
    '!autorepeat-': None,
    }  # type: Mapping[str, Optional[Callable[[ChatCommandArgs], bool]]]
noCommandPreCustom = []  # type: List[Callable[[ChatCommandArgs], bool]]
noCommandPostCustom = []  # type: List[Callable[[ChatCommandArgs], bool]]
