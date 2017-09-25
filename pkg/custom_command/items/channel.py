from typing import Iterable, Mapping, Optional

from lib import data
from .. import channel


def filterMessage() -> Iterable[data.ChatCommand]:
    return []


def commands() -> Mapping[str, Optional[data.ChatCommand]]:
    if not hasattr(commands, 'commands'):
        setattr(commands, 'commands', {
            '!global': channel.commandGlobal,
            '!command': channel.commandCommand,
            })
    return getattr(commands, 'commands')


def commandsStartWith() -> Mapping[str, Optional[data.ChatCommand]]:
    return {}


def processNoCommand() -> Iterable[data.ChatCommand]:
    yield channel.customCommands
