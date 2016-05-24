from .public import whisper as publicList
from collections import ChainMap
try:
    from .private import whisper as privateList
except:
    from .private.default import whisper as privateList

if False: # Hints for Intellisense
    commands = privateList.commands
    commands = publicList.commands

commands = ChainMap(privateList.commands, publicList.commands)
