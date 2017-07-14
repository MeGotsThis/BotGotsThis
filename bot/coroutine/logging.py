import asyncio

import aiofiles

import bot

from collections import deque
from typing import Deque, Tuple

from bot import utils

_queue: Deque[Tuple[str, str]] = deque()


async def record_logs() -> None:
    name = 'File Logger'
    print(f'{utils.now()} Starting {name}')
    try:
        while bot.globals.running or _queue:
            if _queue:
                await _process_log()
            await asyncio.sleep(0)
    finally:
        bot.globals.running = False
        print(f'{utils.now()} Ending {name}')


def log(file: str,
        log: str) -> None:
    _queue.append((file, log))


async def _process_log() -> None:
    filename: str
    log: str
    filename, log = _queue.popleft()
    async with aiofiles.open(filename, 'a', encoding='utf-8') as file:
        await file.write(log)
