from .public import manage as publicList
from collections import ChainMap
from source.data import argument
from typing import Mapping, Optional
try:
    from .private import manage as privateList
except ImportError:
    from .private.default import manage as privateList  # type: ignore

methods = ChainMap(privateList.methods, publicList.methods)  # type: Mapping[str, Optional['argument.ManageBotCommand']]
