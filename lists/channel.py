from .public import channel as publicList
from collections import ChainMap
from source import data
from typing import List, Mapping, Optional
try:
    from .private import channel as privateList
except ImportError:
    from .private.default import channel as privateList  # type: ignore

CommandsDict = Mapping[str, Optional[data.ChatCommand]]


def filterMessage() -> List[data.ChatCommand]:
    if privateList.disableFilters():
        return privateList.filterMessage()
    else:
        return publicList.filterMessage() + privateList.filterMessage()


def commands() -> CommandsDict:
    return ChainMap(privateList.commands(), publicList.commands())


def commandsStartWith() -> CommandsDict:
    return ChainMap(privateList.commandsStartWith(),
                    publicList.commandsStartWith())


def processNoCommand() -> List[data.ChatCommand]:
    if privateList.disableCustomMessage():
        return (privateList.noCommandPreCustom()
                + privateList.noCommandPostCustom())
    else:
        return (privateList.noCommandPreCustom()
                + publicList.processNoCommand()
                + privateList.noCommandPostCustom())
