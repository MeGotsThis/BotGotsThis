from bot import config, globals
from ..library import channel, exit, managebot
from ..library.chat import permission, ownerChannel, send
import datetime
import json
import sys
import time

@ownerChannel
@permission('owner')
def commandExit(args):
    exit.botExit(send(args.chat))
    return True

@ownerChannel
@permission('owner')
def commandSay(args):
    if len(args.message) < 3:
        return False
    if args.message.lower[1] in globals.channels:
        channel.botSay(args.database, args.nick, args.message.lower[1],
                       args.message[2:])
    return True

@ownerChannel
@permission('admin')
def commandJoin(args):
    if len(args.message) < 2:
        return False

    channel.botJoin(args.database, args.message.lower[1], send(args.chat))
    return True

@ownerChannel
@permission('admin')
def commandPart(args):
    if len(args.message) < 2:
        return False
    
    channel.botPart(args.message.lower[1], send(args.chat))
    return True

@ownerChannel
@permission('admin')
def commandEmptyAll(args):
    channel.botEmptyAll(send(args.chat))
    return True

@ownerChannel
@permission('admin')
def commandEmpty(args):
    if len(args.message) < 2:
        return False
    
    channel.botEmpty(args.message.lower[1], send(args.chat))
    return True

@ownerChannel
@permission('owner')
def commandManageBot(args):
    if len(args.message) < 2:
        return False
    
    return managebot.botManageBot(args.database, send(args.chat), args.nick,
                                  args.message)
