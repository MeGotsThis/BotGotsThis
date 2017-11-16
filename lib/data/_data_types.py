from datetime import datetime
from typing import NamedTuple, Optional, Union


class AutoJoinChannel(NamedTuple):
    broadcaster: str
    priority: Union[int, float]


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
