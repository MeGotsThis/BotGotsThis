from datetime import datetime
from typing import Dict, NamedTuple, Optional, Sequence, Union


class AutoJoinChannel(NamedTuple):
    broadcaster: str
    priority: Union[int, float]
    cluster: str


class AutoRepeatMessage(NamedTuple):
    broadcaster: str
    name: str
    message: str


class AutoRepeatList(NamedTuple):
    name: str
    message: str
    remaining: Optional[int]
    duration: float
    last: datetime


class RepeatData(NamedTuple):
    broadcaster: str
    name: str
    message: str
    remaining: Optional[int]
    duration: float
    last: datetime


CommandProperty = Union[str, Sequence[str]]
CommandReturn = Union[str, Dict[str, str]]
