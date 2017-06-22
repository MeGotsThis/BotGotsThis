import asyncio

import aiofiles

import bot.globals

from collections import deque
from typing import Deque, IO, Tuple

from bot import utils

_queue: Deque[Tuple[str, str]] = deque()


async def record_logs():
    name = 'File Logger'
    print('{time} Starting {name}'.format(time=utils.now(), name=name))
    try:
        while bot.globals.running:
            if _queue:
                await _process_log()
            await asyncio.sleep(0)
    finally:
        bot.globals.running = False
        print('{time} Ending {name}'.format(time=utils.now(), name=name))


def log(file: str,
        log: str) -> None:
    _queue.append((file, log))


async def _process_log() -> None:
    filename: str
    log: str
    filename, log = _queue.popleft()
    file = aiofiles.open(filename, 'a', encoding='utf-8')
    async with file:
        await file.write(log)
