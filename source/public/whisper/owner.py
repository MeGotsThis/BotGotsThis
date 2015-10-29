from ..common import channel, exit, managebot
from bot import globals

def sendMessage(nick):
    return lambda m, p=1: globals.queueWhisper(nick, m, p)

def commandHello(nick, message, msgParts, permissions):
    globals.queueWhisper(nick, 'Hello Kappa')
    return True

def commandExit(nick, message, msgParts, permissions):
    exit.botExit(sendMessage(nick))
    return True

def commandSay(nick, message, msgParts, permissions):
    msgParts = message.split(None, 2)
    msgParts[1] = msgParts[1].lower()
    if msgParts[1][0] != '#':
        msgParts[1] = '#' + msgParts[1]
    if msgParts[1] in globals.channels:
        channel.botSay(msgParts[1], msgParts[2])
    return True

def commandJoin(nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False

    chan = msgParts[1].lower()
    if chan[0] != '#':
        chan = '#' + chan
    
    channel.botJoin(chan, sendMessage(nick))
    return True

def commandPart(nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    chan = msgParts[1].lower()
    if chan[0] != '#':
        chan = '#' + chan
    channel.botPart(chan, sendMessage(nick))
    return True

def commandEmptyAll(nick, message, msgParts, permissions):
    channel.botEmptyAll(sendMessage(nick))
    return True

def commandEmpty(nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    if msgParts[1][0] != '#':
        msgParts[1] = '#' + msgParts[1].lower()
    channel.botEmpty(msgParts[1], sendMessage(nick))
    return True

def commandManageBot(nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    
    return managebot.botManageBot(sendMessage(nick), nick, message, msgParts)
