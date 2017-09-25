from typing import Mapping, Optional

from lib import data
from .. import whisper


def commands() -> Mapping[str, Optional[data.WhisperCommand]]:
    if not hasattr(commands, 'commands'):
        setattr(commands, 'commands', {
            '!leave': whisper.commandLeave,
            '!come': whisper.commandCome,
            '!autojoin': whisper.commandAutoJoin,
            })
    return getattr(commands, 'commands')


def commandsStartWith() -> Mapping[str, Optional[data.WhisperCommand]]:
    return {}
