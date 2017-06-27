from source.data import WhisperCommand
from typing import Mapping, Optional


def commands() -> Mapping[str, Optional[WhisperCommand]]:
    if not hasattr(commands, 'commands'):
        setattr(commands, 'commands', {
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
            })
    return getattr(commands, 'commands')


def commandsStartWith() -> Mapping[str, Optional[WhisperCommand]]:
    return {}
