from .public import whisper as publicList
try:
    from .private import whisper as privateList
except:
    from .private.default import whisper as privateList

if False: # Hints for Intellisense
    commands = privateList.commands
    commands = publicList.commands

commands = dict(list(publicList.commands.items()) +
                list(privateList.commands.items()))
