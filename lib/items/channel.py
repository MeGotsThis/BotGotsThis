import importlib
from collections import ChainMap
from typing import Any, Iterable, List, Mapping, Optional  # noqa: F401

import bot
from lib import data

CommandsDict = Mapping[str, Optional[data.ChatCommand]]


def filterMessage() -> Iterable[data.ChatCommand]:
    pkg: str
    for pkg in bot.globals.pkgs:
        channel: Any
        channel = importlib.import_module('pkg.' + pkg + '.items.channel')
        yield from channel.filterMessage()


def commands() -> CommandsDict:
    cmds: List[CommandsDict] = []
    pkg: str
    for pkg in bot.globals.pkgs:
        channel: Any
        channel = importlib.import_module('pkg.' + pkg + '.items.channel')
        ccommands: CommandsDict = channel.commands()
        if ccommands:
            cmds.append(ccommands)
    return ChainMap(*cmds)


def commandsStartWith() -> CommandsDict:
    cmds: List[CommandsDict] = []
    pkg: str
    for pkg in bot.globals.pkgs:
        channel: Any
        channel = importlib.import_module('pkg.' + pkg + '.items.channel')
        ccommands: CommandsDict = channel.commandsStartWith()
        if ccommands:
            cmds.append(ccommands)
    return ChainMap(*cmds)


def processNoCommand() -> Iterable[data.ChatCommand]:
    pkg: str
    for pkg in bot.globals.pkgs:
        channel: Any
        channel = importlib.import_module('pkg.' + pkg + '.items.channel')
        yield from channel.processNoCommand()
