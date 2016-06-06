from .public import manage as publicList
from collections import ChainMap
try:
    from .private import manage as privateList
except ImportError:
    from .private.default import manage as privateList

if False: # Hints for Intellisense
    methods = privateList.methods
    methods = publicList.methods

methods = ChainMap(privateList.methods, publicList.methods)
