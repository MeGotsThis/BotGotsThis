from ..common import channel, exit, managebot, send
from bot import globals

def commandHello(db, nick, message, msgParts, permissions):
    globals.messaging.queueWhisper(nick, 'Hello Kappa')
    return True

def commandExit(db, nick, message, msgParts, permissions):
    exit.botExit(send.whisper(nick))
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
    
    channel.botJoin(db, chan, send.whisper(nick))
    return True

def commandPart(db, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    channel.botPart(msgParts[1].lower(), send.whisper(nick))
    return True

def commandEmptyAll(db, nick, message, msgParts, permissions):
    channel.botEmptyAll(send.whisper(nick))
    return True

def commandEmpty(db, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    channel.botEmpty(msgParts[1].lower(), send.whisper(nick))
    return True

def commandManageBot(db, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    
    return managebot.botManageBot(db, send.whisper(nick), nick, message,
                                  msgParts)
