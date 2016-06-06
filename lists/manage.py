from .public import manage as publicList
from collections import ChainMap
from source.data.argument import ManageBotArgs
from typing import Callable, Mapping, Optional
try:
    from .private import manage as privateList
except ImportError:
    from .private.default import manage as privateList  # type: ignore

methods = ChainMap(privateList.methods, publicList.methods)  # type: Mapping[str, Optional[Callable[[ManageBotArgs], bool]]]
