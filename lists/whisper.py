import importlib
from collections import ChainMap
from typing import Any, List, Mapping, Optional  # noqa: F401

import bot
from lib import data

WhisperDict = Mapping[str, Optional[data.WhisperCommand]]


def commands() -> WhisperDict:
    cmds: List[WhisperDict] = []
    pkg: str
    for pkg in bot.globals.pkgs:
        whisper: Any
        whisper = importlib.import_module('pkg.' + pkg + '.items.whisper')
        ccommands: WhisperDict = whisper.commands()
        if ccommands:
            cmds.append(ccommands)
    return ChainMap(*cmds)


def commandsStartWith() -> WhisperDict:
    cmds: List[WhisperDict] = []
    pkg: str
    for pkg in bot.globals.pkgs:
        whisper: Any
        whisper = importlib.import_module('pkg.' + pkg + '.items.whisper')
        ccommands: WhisperDict = whisper.commandsStartWith()
        if ccommands:
            cmds.append(ccommands)
    return ChainMap(*cmds)
