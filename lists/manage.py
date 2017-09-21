import importlib
from collections import ChainMap
from typing import Any, List, Mapping, Optional  # noqa: F401

import bot
from source import data

MethodDict = Mapping[str, Optional[data.ManageBotCommand]]


def methods() -> MethodDict:
    mthds: List[MethodDict] = []
    pkg: str
    for pkg in bot.globals.pkgs:
        manage: Any
        manage = importlib.import_module('pkg.' + pkg + '.items.manage')
        mthds.append(manage.methods())
    return ChainMap(*mthds)
