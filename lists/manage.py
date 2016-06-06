from .public import manage as publicList
from collections import ChainMap
try:
    from .private import manage as privateList
except ImportError:
    from .private.default import manage as privateList

methods = ChainMap(privateList.methods, publicList.methods)
