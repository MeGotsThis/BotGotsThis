from source.data import WhisperCommand
from typing import Mapping, Optional


def commands() -> Mapping[str, Optional[WhisperCommand]]:
    return {
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
        }


def commandsStartWith() -> Mapping[str, Optional[WhisperCommand]]:
    return {}
