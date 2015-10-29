from bot import config, globals
from ..common import channel, exit, managebot
import datetime
import json
import sys
import time

def commandExit(channelData, nick, message, msgParts, permissions):
    exit.botExit(channelData.sendMessage)
    return True

def commandSay(channelData, nick, message, msgParts, permissions):
    msgParts = message.split(None, 2)
    msgParts[1] = msgParts[1].lower()
    if msgParts[1][0] != '#':
        msgParts[1] = '#' + msgParts[1]
    if msgParts[1] in globals.channels:
        channel.botSay(msgParts[1], msgParts[2])
    return True

def commandJoin(channelData, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False

    chan = msgParts[1].lower()
    if chan[0] != '#':
        chan = '#' + chan
    
    channel.botJoin(chan, channelData.sendMessage)
    return True

def commandPart(channelData, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    chan = msgParts[1].lower()
    if chan[0] != '#':
        chan = '#' + chan
    channel.botPart(chan, channelData.sendMessage)
    return True

def commandEmptyAll(channelData, nick, message, msgParts, permissions):
    channel.botEmptyAll(channelData.sendMessage)
    return True

def commandEmpty(channelData, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    if msgParts[1][0] != '#':
        msgParts[1] = '#' + msgParts[1].lower()
    channel.botEmpty(msgParts[1], channelData.sendMessage)
    return True

def commandManageBot(channelData, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    
    return managebot.botManageBot(channelData.sendMessage,
                                  nick, message, msgParts)
