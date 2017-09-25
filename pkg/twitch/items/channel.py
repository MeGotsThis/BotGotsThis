from typing import Iterable, Mapping, Optional

from lib import data
from .. import channel


def filterMessage() -> Iterable[data.ChatCommand]:
    return []


def commands() -> Mapping[str, Optional[data.ChatCommand]]:
    if not hasattr(commands, 'commands'):
        setattr(commands, 'commands', {
            '!uptime': channel.commandUptime,
            '!status': channel.commandStatus,
            '!title': channel.commandStatus,
            '!game': channel.commandGame,
            '!setgame': channel.commandRawGame,
            '!community': channel.commandCommunity,
            })
    return getattr(commands, 'commands')


def commandsStartWith() -> Mapping[str, Optional[data.ChatCommand]]:
    return {}


def processNoCommand() -> Iterable[data.ChatCommand]:
    return []
