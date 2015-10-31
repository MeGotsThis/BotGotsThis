from ..common import channel, exit, managebot
from bot import globals

def sendMessage(nick):
    return lambda m, p=1: globals.messaging.queueWhisper(nick, m, p)

def commandHello(db, nick, message, msgParts, permissions):
    globals.messaging.queueWhisper(nick, 'Hello Kappa')
    return True

def commandExit(db, nick, message, msgParts, permissions):
    exit.botExit(sendMessage(nick))
    return True

def commandSay(db, nick, message, msgParts, permissions):
    msgParts = message.split(None, 2)
    msgParts[1] = msgParts[1].lower()
    if msgParts[1] in globals.channels:
        channel.botSay(msgParts[1], msgParts[2])
    return True

def commandJoin(db, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False

    chan = msgParts[1].lower()
    
    channel.botJoin(db, chan, sendMessage(nick))
    return True

def commandPart(db, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    channel.botPart(msgParts[1].lower(), sendMessage(nick))
    return True

def commandEmptyAll(db, nick, message, msgParts, permissions):
    channel.botEmptyAll(sendMessage(nick))
    return True

def commandEmpty(db, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    channel.botEmpty(msgParts[1].lower(), sendMessage(nick))
    return True

def commandManageBot(db, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    
    return managebot.botManageBot(db, sendMessage(nick), nick, message,
                                  msgParts)
