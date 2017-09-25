from typing import Iterable, Mapping, Optional

from lib import data
from ..channel import broadcaster


def filterMessage() -> Iterable[data.ChatCommand]:
    return []


def commands() -> Mapping[str, Optional[data.ChatCommand]]:
    if not hasattr(commands, 'commands'):
        setattr(commands, 'commands', {
            '!hello': broadcaster.commandHello,
            '!leave': broadcaster.commandLeave,
            '!come': broadcaster.commandCome,
            '!autojoin': broadcaster.commandAutoJoin,
            })
    return getattr(commands, 'commands')


def commandsStartWith() -> Mapping[str, Optional[data.ChatCommand]]:
    return {}


def processNoCommand() -> Iterable[data.ChatCommand]:
    return []
