import bot.globals
import time
from bot import utils
from ...data import Send


def exit(send: Send) -> bool:
    send('Goodbye Keepo')
    time.sleep(0.5)
    channel: str
    for channel in set(bot.globals.channels.keys()):
        utils.partChannel(channel)
    bot.globals.running = False
    return True
