from bot import config, globals
from ..library import channel, exit, managebot, send
import datetime
import json
import sys
import time

def commandExit(args):
    exit.botExit(send.channel(args.chat))
    return True

def commandSay(args):
    if len(args.message) < 3:
        return False
    if args.message.lower[1] in globals.channels:
        channel.botSay(args.database, args.nick, args.message.lower[1],
                       args.message[2:])
    return True

def commandJoin(args):
    if len(args.message) < 2:
        return False

    channel.botJoin(args.database, args.message.lower[1],
                    send.channel(args.chat))
    return True

def commandPart(args):
    if len(args.message) < 2:
        return False
    
    channel.botPart(args.message.lower[1], send.channel(args.chat))
    return True

def commandEmptyAll(args):
    channel.botEmptyAll(send.channel(args.chat))
    return True

def commandEmpty(args):
    if len(args.message) < 2:
        return False
    
    channel.botEmpty(args.message.lower[1], send.channel(args.chat))
    return True

def commandManageBot(args):
    if len(args.message) < 2:
        return False
    
    return managebot.botManageBot(args.database, send.channel(args.chat),
                                  args.nick, args.message)
