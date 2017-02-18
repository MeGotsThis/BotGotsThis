from source.data import ChatCommand
from typing import List, Mapping, Optional

disableFilters: bool = True
disableCustomMessage: bool = True

filterMessage: List[ChatCommand] = []
commands: Mapping[str, Optional[ChatCommand]] = {
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
    }
commandsStartWith: Mapping[str, Optional[ChatCommand]] = {
    '!pyramid-': None,
    '!wall-': None,
    '!autorepeat-': None,
    }
noCommandPreCustom: List[ChatCommand] = []
noCommandPostCustom: List[ChatCommand] = []
