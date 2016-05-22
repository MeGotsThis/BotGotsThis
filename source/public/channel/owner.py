from bot import config, globals
from ..common import channel, exit, managebot, send
import datetime
import json
import sys
import time

def commandExit(db, chat, tags, nick, message, tokens, permissions, now):
    exit.botExit(send.channel(chat))
    return True

def commandSay(db, chat, tags, nick, message, tokens, permissions, now):
    tokens = message.split(None, 2)
    tokens[1] = tokens[1].lower()
    if tokens[1] in globals.channels:
        channel.botSay(db, nick, tokens[1], tokens[2])
    return True

def commandJoin(db, chat, tags, nick, message, tokens, permissions, now):
    if len(tokens) < 2:
        return False

    chan = tokens[1].lower()
    channel.botJoin(db, chan, send.channel(chat))
    return True

def commandPart(db, chat, tags, nick, message, tokens, permissions, now):
    if len(tokens) < 2:
        return False
    chan = tokens[1].lower()
    channel.botPart(chan, send.channel(chat))
    return True

def commandEmptyAll(db, chat, tags, nick, message, tokens, permissions, now):
    channel.botEmptyAll(send.channel(chat))
    return True

def commandEmpty(db, chat, tags, nick, message, tokens, permissions, now):
    if len(tokens) < 2:
        return False
    channel.botEmpty(tokens[1], send.channel(chat))
    return True

def commandManageBot(db, chat, tags, nick, message, tokens, permissions, now):
    if len(tokens) < 2:
        return False
    
    return managebot.botManageBot(db, send.channel(chat), nick, message,
                                  tokens)
