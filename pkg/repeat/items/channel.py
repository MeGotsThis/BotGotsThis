from typing import Iterable, Mapping, Optional

from lib import data
from .. import channel


def filterMessage() -> Iterable[data.ChatCommand]:
    return []


def commands() -> Mapping[str, Optional[data.ChatCommand]]:
    if not hasattr(commands, 'commands'):
        setattr(commands, 'commands', {
            '!autorepeat': channel.commandAutoRepeat,
            })
    return getattr(commands, 'commands')


def commandsStartWith() -> Mapping[str, Optional[data.ChatCommand]]:
    if not hasattr(commandsStartWith, 'commands'):
        setattr(commandsStartWith, 'commands', {
            '!autorepeat-': channel.commandAutoRepeat,
            })
    return getattr(commandsStartWith, 'commands')


def processNoCommand() -> Iterable[data.ChatCommand]:
    return []
