from typing import Iterable, Mapping, Optional

from lib import data
from ..channel import block_url
from ..channel import purge


def filterMessage() -> Iterable[data.ChatCommand]:
    yield block_url.filterNoUrlForBots


def commands() -> Mapping[str, Optional[data.ChatCommand]]:
    if not hasattr(commands, 'commands'):
        setattr(commands, 'commands', {
            '!purge': purge.commandPurge,
            })
    return getattr(commands, 'commands')


def commandsStartWith() -> Mapping[str, Optional[data.ChatCommand]]:
    return {}


def processNoCommand() -> Iterable[data.ChatCommand]:
    return []
