from config import config
import ircbot.irc
import datetime
import time
import sys

def commandExit(channelThread, nick, message, msgParts, permissions):
    sys.exit(0)
    return True

def commandSay(channelThread, nick, message, msgParts, permissions):
    if (permissions['owner'] and permissions['ownerChan']):
        msgParts = message.split(None, 2)
        if msgParts[1][0] != '#':
            msgParts[1] = '#' + msgParts[1]
        if msgParts[1] in ircbot.irc.channels:
            ircbot.irc.channels[msgParts[1]].sendMessage(msgParts[2])
        return True
    return False

def commandJoin(channelThread, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    chan = msgParts[1].lower()
    if chan[0] != '#':
        chan = '#' + chan
    if ircbot.irc.joinChannel(chan):
        channelThread.sendMessage('Joining ' + chan[1:])
    else:
        channelThread.sendMessage('Already joined ' + chan[1:])
    return True

def commandPart(channelThread, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    chan = msgParts[1].lower()
    if chan[0] != '#':
        chan = '#' + chan
    ircbot.irc.partChannel(chan)
    channelThread.sendMessage('Leaving ' + chan[1:])
    return True

def commandEmptyAll(channelThread, nick, message, msgParts, permissions):
    ircbot.irc.messaging.clearAllQueue()
    channelThread.sendMessage('Cleared all queued msgs')
    return True

def commandEmpty(channelThread, nick, message, msgParts, permissions):
    if msgParts[1][0] != '#':
        msgParts[1] = '#' + msgParts[1]
    ircbot.irc.messaging.clearQueue(msgParts[1])
    channelThread.sendMessage(
        'Cleared all queued messages for ' + msgParts[1][1:])
    return True

