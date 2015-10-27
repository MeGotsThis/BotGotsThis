import ircbot.irc
import time

def botExit(sendMessage):
    sendMessage('Goodbye Keepo', 0)
    time.sleep(0.5)
    for channel in set(ircbot.irc.channels.keys()):
        ircbot.irc.partChannel(channel)
    ircbot.irc.messaging.running = False
