from bot import globals, utils
from ...data import Send
import time


def exit(send: Send) -> bool:
    send('Goodbye Keepo')
    time.sleep(0.5)
    for channel in set(globals.channels.keys()):  # --type: str
        utils.partChannel(channel)
    globals.running = False
    return True
