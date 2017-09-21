import importlib
from collections import ChainMap
from typing import Any, List, Mapping, Optional  # noqa: F401

import bot

FeatureDict = Mapping[str, Optional[str]]


def features() -> FeatureDict:
    ftrs: List[FeatureDict] = []
    pkg: str
    for pkg in bot.globals.pkgs:
        feature: Any
        feature = importlib.import_module('pkg.' + pkg + '.items.feature')
        ftrs.append(feature.methods())
    return ChainMap(*ftrs)
