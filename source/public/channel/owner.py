from bot import config, globals
from ..common import channel, exit, managebot, send
import datetime
import json
import sys
import time

def commandExit(db, chat, tags, nick, message, msgParts, permissions, now):
    exit.botExit(send.channel(chat))
    return True

def commandSay(db, chat, tags, nick, message, msgParts, permissions, now):
    msgParts = message.split(None, 2)
    msgParts[1] = msgParts[1].lower()
    if msgParts[1] in globals.channels:
        channel.botSay(msgParts[1], msgParts[2])
    return True

def commandJoin(db, chat, tags, nick, message, msgParts, permissions, now):
    if len(msgParts) < 2:
        return False

    chan = msgParts[1].lower()
    channel.botJoin(db, chan, send.channel(chat))
    return True

def commandPart(db, chat, tags, nick, message, msgParts, permissions, now):
    if len(msgParts) < 2:
        return False
    chan = msgParts[1].lower()
    channel.botPart(chan, send.channel(chat))
    return True

def commandEmptyAll(db, chat, tags, nick, message, msgParts, permissions, now):
    channel.botEmptyAll(send.channel(chat))
    return True

def commandEmpty(db, chat, tags, nick, message, msgParts, permissions, now):
    if len(msgParts) < 2:
        return False
    channel.botEmpty(msgParts[1], send.channel(chat))
    return True

def commandManageBot(db, chat, tags, nick, message, msgParts, permissions, now):
    if len(msgParts) < 2:
        return False
    
    return managebot.botManageBot(db, send.channel(chat), nick, message,
                                  msgParts)
