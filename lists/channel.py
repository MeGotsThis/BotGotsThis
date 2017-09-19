from pkg.botgotsthis.items import channel as publicList
from collections import ChainMap
from source import data
from typing import Iterable, Mapping, Optional
try:
    from .private import channel as privateList
except ImportError:
    from .private.default import channel as privateList  # type: ignore

CommandsDict = Mapping[str, Optional[data.ChatCommand]]


def filterMessage() -> Iterable[data.ChatCommand]:
    yield from privateList.filterMessage()
    if not privateList.disableFilters():
        yield from publicList.filterMessage()


def commands() -> CommandsDict:
    return ChainMap(privateList.commands(), publicList.commands())


def commandsStartWith() -> CommandsDict:
    return ChainMap(privateList.commandsStartWith(),
                    publicList.commandsStartWith())


def processNoCommand() -> Iterable[data.ChatCommand]:
    yield from privateList.noCommand()
    if not privateList.disableCustomMessage():
        yield from publicList.processNoCommand()
