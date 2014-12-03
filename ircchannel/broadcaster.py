from config import config
import ircbot.twitchApi
import ircbot.irc
import time

def commandHello(channelData, nick, message, msgParts, permissions):
    channelData.sendMessage('Hello Kappa')
    return True

def commandCome(channelData, nick, message, msgParts, permissions):
    if ('#' + nick) in ircbot.irc.channels:
        channelData.sendMessage('I am already in ' + nick)
        return True
    channelData.sendMessage('Joining ' + nick)
    ircbot.irc.joinChannel(nick)
    return True

def commandLeave(channelData, nick, message, msgParts, permissions):
    if channelData.channel == '#' + config.botnick:
        return False
    channelData.sendMessage('Bye ' + channelData.channel[1:])
    time.sleep(1)
    ircbot.irc.partChannel(channelData.channel)
    return True

def commandEmpty(channelData, nick, message, msgParts, permissions):
    ircbot.irc.messaging.clearQueue(channelData.channel)
    channelData.sendMessage(
        'Cleared all queued messages for ' + channelData.channel[1:])
    return True

