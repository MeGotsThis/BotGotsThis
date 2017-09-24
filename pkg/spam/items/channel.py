from typing import Iterable, Mapping, Optional

from lib import data
from ..channel import pyramid
from ..channel import wall


def filterMessage() -> Iterable[data.ChatCommand]:
    return []


def commands() -> Mapping[str, Optional[data.ChatCommand]]:
    if not hasattr(commands, 'commands'):
        setattr(commands, 'commands', {
            '!pyramid': pyramid.commandPyramid,
            '!rpyramid': pyramid.commandRandomPyramid,
            '!wall': wall.commandWall,
            })
    return getattr(commands, 'commands')


def commandsStartWith() -> Mapping[str, Optional[data.ChatCommand]]:
    if not hasattr(commandsStartWith, 'commands'):
        setattr(commandsStartWith, 'commands', {
            '!pyramid-': pyramid.commandPyramidLong,
            '!wall-': wall.commandWallLong,
            })
    return getattr(commandsStartWith, 'commands')


def processNoCommand() -> Iterable[data.ChatCommand]:
    return []
