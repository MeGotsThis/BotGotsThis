from .public import manage as publicList
from collections import ChainMap
from source import data
from typing import Mapping, Optional
try:
    from .private import manage as privateList
except ImportError:
    from .private.default import manage as privateList  # type: ignore

MethodDict = Mapping[str, Optional[data.ManageBotCommand]]

methods = ChainMap(privateList.methods, publicList.methods)  # type: MethodDict
