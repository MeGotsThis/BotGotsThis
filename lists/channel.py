from .public import channel as publicList
from collections import ChainMap
from source import data
from typing import List, Mapping, Optional
try:
    from .private import channel as privateList
except ImportError:
    from .private.default import channel as privateList  # type: ignore

CommandsDict = Mapping[str, Optional[data.ChatCommand]]

filterMessage: List[data.ChatCommand] = []
commands: CommandsDict
commandsStartWith: CommandsDict
processNoCommand: List[data.ChatCommand]

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
