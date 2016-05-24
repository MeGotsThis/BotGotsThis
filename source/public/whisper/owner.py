from ..common import channel, exit, managebot, send
from bot import globals

def commandHello(db, nick, message, permissions, now):
    globals.messaging.queueWhisper(nick, 'Hello Kappa')
    return True

def commandExit(db, nick, message, permissions, now):
    exit.botExit(send.whisper(nick))
    return True

def commandSay(db, nick, message, permissions, now):
    if message.lower[1] in globals.channels:
        channel.botSay(db, nick, message.lower[1], message[2:])
    return True

def commandJoin(db, nick, message, permissions, now):
    if len(message) < 2:
        return False

    chan = message.lower[1]
    
    channel.botJoin(db, chan, send.whisper(nick))
    return True

def commandPart(db, nick, message, permissions, now):
    if len(message) < 2:
        return False
    channel.botPart(message.lower[1], send.whisper(nick))
    return True

def commandEmptyAll(db, nick, message, permissions, now):
    channel.botEmptyAll(send.whisper(nick))
    return True

def commandEmpty(db, nick, message, permissions, now):
    if len(message) < 2:
        return False
    channel.botEmpty(message.lower[1], send.whisper(nick))
    return True

def commandManageBot(db, nick, message, permissions, now):
    if len(message) < 2:
        return False
    
    return managebot.botManageBot(db, send.whisper(nick), nick, message)
