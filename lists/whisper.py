from .public import whisper as publicList
from collections import ChainMap
try:
    from .private import whisper as privateList
except ImportError:
    from .private.default import whisper as privateList

commands = ChainMap(privateList.commands, publicList.commands)
