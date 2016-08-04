import bot.globals
import time
from bot import utils
from ...data import Send


def exit(send: Send) -> bool:
    send('Goodbye Keepo')
    time.sleep(0.5)
    for channel in set(bot.globals.channels.keys()):  # --type: str
        utils.partChannel(channel)
    bot.globals.running = False
    return True
