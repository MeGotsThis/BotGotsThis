import asyncio

import bot

from datetime import datetime, timedelta
from typing import Awaitable, Callable, List
from bot import utils

_tasks: List['Task'] = []


class Task:
    def __init__(self,
                 task: Callable[[datetime], Awaitable[None]],
                 interval: timedelta) -> None:
        if not callable(task):
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


async def background_tasks():
    name = 'Background Tasker'
    print(f'{utils.now()} Starting {name}')
    while bot.globals.running:
        await asyncio.sleep(0)
        run_tasks()
    print(f'{utils.now()} Ending {name}')


def run_tasks():
    timestamp: datetime = utils.now()
    task: Task
    for task in _tasks[:]:
        if timestamp >= task.timestamp + task.interval:
            asyncio.ensure_future(_run_task(task.task, timestamp))
            task.timestamp = timestamp


async def _run_task(task: Callable[[datetime], Awaitable[None]],
                    timestamp: datetime) -> None:
    try:
        await task(timestamp)
    except:
        utils.logException()


def add_task(task: Callable[[datetime], Awaitable[None]],
             interval: timedelta=timedelta(seconds=60)) -> None:
    _tasks.append(Task(task, interval))
