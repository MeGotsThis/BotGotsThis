from lib import data
from ..whisper import broadcaster
from typing import Mapping, Optional


def commands() -> Mapping[str, Optional[data.WhisperCommand]]:
    if not hasattr(commands, 'commands'):
        setattr(commands, 'commands', {
            '!leave': broadcaster.commandLeave,
            '!come': broadcaster.commandCome,
            '!autojoin': broadcaster.commandAutoJoin,
            })
    return getattr(commands, 'commands')


def commandsStartWith() -> Mapping[str, Optional[data.WhisperCommand]]:
    return {}
