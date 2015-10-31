from bot import globals, utils
import time

def botExit(send):
    send('Goodbye Keepo', 0)
    time.sleep(0.5)
    for channel in set(globals.channels.keys()):
        utils.partChannel(channel)
    globals.messaging.running = False
