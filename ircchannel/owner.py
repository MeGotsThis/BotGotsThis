from config import config
import botcommands.channel
import botcommands.exit
import botcommands.managebot
import database.factory
import ircbot.twitchApi
import ircbot.irc
import datetime
import time
import json
import sys

def commandExit(channelData, nick, message, msgParts, permissions):
    botcommands.exit.botExit(channelData.sendMessage)
    return True

def commandSay(channelData, nick, message, msgParts, permissions):
    msgParts = message.split(None, 2)
    msgParts[1] = msgParts[1].lower()
    if msgParts[1][0] != '#':
        msgParts[1] = '#' + msgParts[1]
    if msgParts[1] in ircbot.irc.channels:
        botcommands.channel.botSay(msgParts[1], msgParts[2])
    return True

def commandJoin(channelData, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False

    chan = msgParts[1].lower()
    if chan[0] != '#':
        chan = '#' + chan
    
    botcommands.channel.botJoin(chan, channelData.sendMessage)
    return True

def commandPart(channelData, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    chan = msgParts[1].lower()
    if chan[0] != '#':
        chan = '#' + chan
    botcommands.channel.botPart(chan, channelData.sendMessage)
    return True

def commandEmptyAll(channelData, nick, message, msgParts, permissions):
    botcommands.channel.botEmptyAll(channelData.sendMessage)
    return True

def commandEmpty(channelData, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    if msgParts[1][0] != '#':
        msgParts[1] = '#' + msgParts[1].lower()
    botcommands.channel.botEmpty(msgParts[1], channelData.sendMessage)
    return True

def commandManageBot(channelData, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    
    return botcommands.managebot.botManageBot(channelData.sendMessage,
                                              nick, message, msgParts)
