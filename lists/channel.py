from .public import channel as publicList
from collections import ChainMap
from source import data
from typing import List, Mapping, Optional
try:
    from .private import channel as privateList
except ImportError:
    from .private.default import channel as privateList  # type: ignore

filterMessage = []  # type: List[data.ChatCommand]
if privateList.disableFilters:
    filterMessage = privateList.filterMessage
else:
    filterMessage = publicList.filterMessage + privateList.filterMessage
commands = ChainMap(privateList.commands, publicList.commands)  # type: Mapping[str, Optional[data.ChatCommand]]
commandsStartWith = ChainMap(privateList.commandsStartWith,
                             publicList.commandsStartWith)  # type: Mapping[str, Optional[data.ChatCommand]]
processNoCommand = privateList.noCommandPreCustom  # type: List[data.ChatCommand]
if not privateList.disableCustomMessage:
    processNoCommand += publicList.processNoCommand
processNoCommand += privateList.noCommandPostCustom
