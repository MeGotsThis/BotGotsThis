import importlib
from typing import Any, Collection, Iterable, List  # noqa: F401

import bot
from lib import data


def fields() -> Iterable[data.CustomCommandField]:
    pkg: str
    for pkg in bot.globals.pkgs:
        custom: Any
        custom = importlib.import_module('pkg.' + pkg + '.items.custom')
        yield from custom.fields()


def properties() -> Collection[str]:
    props: List[str] = []
    pkg: str
    for pkg in bot.globals.pkgs:
        custom: Any
        custom = importlib.import_module('pkg.' + pkg + '.items.custom')
        props.extend(custom.properties())
    return props


def postProcess() -> Iterable[data.CustomCommandProcess]:
    pkg: str
    for pkg in bot.globals.pkgs:
        custom: Any
        custom = importlib.import_module('pkg.' + pkg + '.items.custom')
        yield from custom.postProcess()
