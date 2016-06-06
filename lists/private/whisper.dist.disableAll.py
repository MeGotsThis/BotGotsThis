from source.data.argument import WhisperCommandArgs
from typing import Callable, Mapping, Optional

commands = {
    '!hello': None,
    '!exit': None,
    '!say': None,
    '!join': None,
    '!part': None,
    '!emptychat': None,
    '!emptyall': None,
    '!managebot': None,
    '!reload': None,
    '!reloadcommands': None,
    '!reloadconfig': None,
    '!leave': None,
    '!empty': None,
    '!come': None,
    '!autojoin': None,
    '!feature': None,
    }  # type: Mapping[str, Optional[Callable[[WhisperCommandArgs], bool]]]
