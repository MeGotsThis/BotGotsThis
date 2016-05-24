from bot import config, globals
from ..library import channel, exit, managebot, send
import datetime
import json
import sys
import time

def commandExit(db, chat, tags, nick, message, permissions, now):
    exit.botExit(send.channel(chat))
    return True

def commandSay(db, chat, tags, nick, message, permissions, now):
    if len(message) < 3:
        return False
    if message.lower[1] in globals.channels:
        channel.botSay(db, nick, message.lower[1], message[2:])
    return True

def commandJoin(db, chat, tags, nick, message, permissions, now):
    if len(message) < 2:
        return False

    channel.botJoin(db, message.lower[1], send.channel(chat))
    return True

def commandPart(db, chat, tags, nick, message, permissions, now):
    if len(message) < 2:
        return False
    
    channel.botPart(message.lower[1], send.channel(chat))
    return True

def commandEmptyAll(db, chat, tags, nick, message, permissions, now):
    channel.botEmptyAll(send.channel(chat))
    return True

def commandEmpty(db, chat, tags, nick, message, permissions, now):
    if len(message) < 2:
        return False
    
    channel.botEmpty(message.lower[1], send.channel(chat))
    return True

def commandManageBot(db, chat, tags, nick, message, permissions, now):
    if len(message) < 2:
        return False
    
    return managebot.botManageBot(db, send.channel(chat), nick, message)
