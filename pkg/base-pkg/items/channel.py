from typing import Iterable, Mapping, Optional

from lib.data import ChatCommand


def filterMessage() -> Iterable[ChatCommand]:
    return []


def commands() -> Mapping[str, Optional[ChatCommand]]:
    return {}


def commandsStartWith() -> Mapping[str, Optional[ChatCommand]]:
    return {}


def processNoCommand() -> Iterable[ChatCommand]:
    return []
