import asyncio

import bot

from bot import utils

from lib.data import Send


async def exit(send: Send) -> bool:
    send('Goodbye Keepo')
    await asyncio.sleep(0.5)
    channel: str
    for channel in set(bot.globals.channels.keys()):
        utils.partChannel(channel)
    bot.globals.running = False
    return True
