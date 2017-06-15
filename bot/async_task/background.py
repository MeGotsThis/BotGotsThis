import asyncio

import bot.globals

from datetime import datetime, timedelta
from typing import Awaitable, Callable, List
from bot import utils

_tasks: List['Task'] = []


class Task:
    def __init__(self,
                 task: Callable[[datetime], Awaitable[None]],
                 interval: timedelta) -> None:
        if not isinstance(task, Callable):  # type: ignore
            raise TypeError()
        if not isinstance(interval, timedelta):
            raise TypeError()
        self._task: Callable[[datetime], Awaitable[None]] = task
        self._interval: timedelta = interval
        self._timestamp: datetime = datetime.min

    @property
    def task(self) -> Callable[[datetime], Awaitable[None]]:
        return self._task

    @property
    def interval(self) -> timedelta:
        return self._interval

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: datetime) -> None:
        if not isinstance(value, datetime):
            raise TypeError()
        self._timestamp = value


async def run_tasks():
    name = 'Background Tasker'
    print('{time} Starting {name}'.format(time=utils.now(), name=name))
    while bot.globals.running:
        await asyncio.sleep(0)
        timestamp: datetime = utils.now()
        task: Task
        for task in _tasks[:]:
            if timestamp >= task.timestamp + task.interval:
                asyncio.ensure_future(_run_task(task.task, timestamp))
                task.timestamp = timestamp
    print('{time} Ending {name}'.format(time=utils.now(), name=name))


async def _run_task(task: Callable[[datetime], Awaitable[None]],
                   timestamp: datetime) -> None:
    try:
        await task(timestamp)
    except:
        utils.logException()


def add_task(task: Callable[[datetime], Awaitable[None]],
             interval: timedelta=timedelta(seconds=60)) -> None:
    _tasks.append(Task(task, interval))
