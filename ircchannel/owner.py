from config import config
import ircbot.irc
import datetime
import time
import sys

def commandExit(channelThread, nick, message, msgParts, permissions):
    channelThread.sendMessage('Goodbye Keepo', 0)
    time.sleep(0.5)
    for channel in set(ircbot.irc.channels.keys()):
        ircbot.irc.partChannel(channel)
    ircbot.irc.messaging.running = False
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

def commandListChats(channelThread, nick, message, msgParts, permissions):
    channels = [c[1:] for c in ircbot.irc.channels.keys()]
    channelThread.sendMessage('Twitch Chats: ' + ', '.join(channels))
    return True
