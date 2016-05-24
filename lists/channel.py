from .public import channel as publicList
from collections import ChainMap
try:
    from .private import channel as privateList
except:
    from .private.default import channel as privateList

if False: # Hints for Intellisense
    filterMessage = privateList.filterMessage
    filterMessage = publicList.filterMessage
    commands = privateList.commands
    commands = publicList.commands
    commandsStartWith = publicList.commandsStartWith
    commandsStartWith = privateList.commandsStartWith
    commandsStartWith = publicList.commandsStartWith
    processNoCommand = privateList.noCommandPreCustom
    processNoCommand = privateList.noCommandPostCustom
    processNoCommand = publicList.processNoCommand

if privateList.disableFilters:
    filterMessage = privateList.filterMessage
else:
    filterMessage = publicList.filterMessage + privateList.filterMessage
commands = ChainMap(privateList.commands, publicList.commands)
commandsStartWith = ChainMap(privateList.commandsStartWith,
                             publicList.commandsStartWith)
processNoCommand = privateList.noCommandPreCustom
if not privateList.disableCustomMessage:
    processNoCommand += publicList.processNoCommand
processNoCommand += privateList.noCommandPostCustom
