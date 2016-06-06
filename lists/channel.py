from .public import channel as publicList
from collections import ChainMap
from source.data.argument import ChatCommandArgs
from typing import Callable, List, Mapping, Optional
try:
    from .private import channel as privateList
except ImportError:
    from .private.default import channel as privateList  # type: ignore

filterMessage = []  # type: List[Callable[[ChatCommandArgs], bool]]
if privateList.disableFilters:
    filterMessage = privateList.filterMessage
else:
    filterMessage = publicList.filterMessage + privateList.filterMessage
commands = ChainMap(privateList.commands, publicList.commands)  # type: Mapping[str, Optional[Callable[[ChatCommandArgs], bool]]]
commandsStartWith = ChainMap(privateList.commandsStartWith,
                             publicList.commandsStartWith)  # type: Mapping[str, Optional[Callable[[ChatCommandArgs], bool]]]
processNoCommand = privateList.noCommandPreCustom  # type: List[Callable[[ChatCommandArgs], bool]]
if not privateList.disableCustomMessage:
    processNoCommand += publicList.processNoCommand
processNoCommand += privateList.noCommandPostCustom
