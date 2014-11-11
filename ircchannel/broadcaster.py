from config import config
import ircbot.twitchApi
import ircbot.irc
import time

def commandHello(channelThread, nick, message, msgParts, permissions):
    channelThread.sendMessage('Hello Kappa')
    return True

def commandLeave(channelThread, nick, message, msgParts, permissions):
    if channelThread.channel == '#' + config.botnick:
        return False
    channelThread.sendMessage('Bye ' + channelThread.channel[1:])
    time.sleep(1)
    ircbot.irc.partChannel(channelThread.channel)
    return True

def commandEmpty(channelThread, nick, message, msgParts, permissions):
    ircbot.irc.messaging.clearQueue(channelThread.channel)
    channelThread.sendMessage(
        'Cleared all queued messages for ' + channelThread.channel[1:])
    return True

