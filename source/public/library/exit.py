from bot import globals, utils
from ...data import Send
import time


def botExit(send: Send) -> None:
    send('Goodbye Keepo')
    time.sleep(0.5)
    for channel in set(globals.channels.keys()):
        utils.partChannel(channel)
    globals.running = False
