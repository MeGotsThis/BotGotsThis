from source.data import ChatCommand
from typing import Iterable, Mapping, Optional


def disableFilters() -> bool:
    return False


def disableCustomMessage() -> bool:
    return False


def filterMessage() -> Iterable[ChatCommand]:
    return []


def commands() -> Mapping[str, Optional[ChatCommand]]:
    return {}


def commandsStartWith() -> Mapping[str, Optional[ChatCommand]]:
    return {}


def noCommand() -> Iterable[ChatCommand]:
    return []
