from lib import data
from .. import whisper
from typing import Mapping, Optional


def commands() -> Mapping[str, Optional[data.WhisperCommand]]:
    if not hasattr(commands, 'commands'):
        setattr(commands, 'commands', {
            '!feature': whisper.commandFeature,
            })
    return getattr(commands, 'commands')


def commandsStartWith() -> Mapping[str, Optional[data.WhisperCommand]]:
    return {}
