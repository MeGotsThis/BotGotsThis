from config import config
import ircbot.irc
import datetime
import time
import sys

def commandExit(channelData, nick, message, msgParts, permissions):
    channelData.sendMessage('Goodbye Keepo', 0)
    time.sleep(0.5)
    for channel in set(ircbot.irc.channels.keys()):
        ircbot.irc.partChannel(channel)
    ircbot.irc.messaging.running = False
    return True

def commandSay(channelData, nick, message, msgParts, permissions):
    if (permissions['owner'] and permissions['ownerChan']):
        msgParts = message.split(None, 2)
        if msgParts[1][0] != '#':
            msgParts[1] = '#' + msgParts[1]
        if msgParts[1] in ircbot.irc.channels:
            ircbot.irc.channels[msgParts[1]].sendMessage(msgParts[2])
        return True
    return False

def commandJoin(channelData, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    chan = msgParts[1].lower()
    if chan[0] != '#':
        chan = '#' + chan
    if ircbot.irc.joinChannel(chan):
        channelData.sendMessage('Joining ' + chan[1:])
    else:
        channelData.sendMessage('Already joined ' + chan[1:])
    return True

def commandPart(channelData, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    chan = msgParts[1].lower()
    if chan[0] != '#':
        chan = '#' + chan
    ircbot.irc.partChannel(chan)
    channelData.sendMessage('Leaving ' + chan[1:])
    return True

def commandEmptyAll(channelData, nick, message, msgParts, permissions):
    ircbot.irc.messaging.clearAllQueue()
    channelData.sendMessage('Cleared all queued msgs')
    return True

def commandEmpty(channelData, nick, message, msgParts, permissions):
    if msgParts[1][0] != '#':
        msgParts[1] = '#' + msgParts[1]
    ircbot.irc.messaging.clearQueue(msgParts[1])
    channelData.sendMessage(
        'Cleared all queued messages for ' + msgParts[1][1:])
    return True

def commandListChats(channelData, nick, message, msgParts, permissions):
    channels = [c[1:] for c in ircbot.irc.channels.keys()]
    channelData.sendMessage('Twitch Chats: ' + ', '.join(channels))
    return True
