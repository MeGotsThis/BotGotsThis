from ..common import channel, exit, managebot, send
from bot import globals

def commandHello(db, nick, message, tokens, permissions, now):
    globals.messaging.queueWhisper(nick, 'Hello Kappa')
    return True

def commandExit(db, nick, message, tokens, permissions, now):
    exit.botExit(send.whisper(nick))
    return True

def commandSay(db, nick, message, tokens, permissions, now):
    tokens = message.split(None, 2)
    tokens[1] = tokens[1].lower()
    if tokens[1] in globals.channels:
        channel.botSay(db, nick, tokens[1], tokens[2])
    return True

def commandJoin(db, nick, message, tokens, permissions, now):
    if len(tokens) < 2:
        return False

    chan = tokens[1].lower()
    
    channel.botJoin(db, chan, send.whisper(nick))
    return True

def commandPart(db, nick, message, tokens, permissions, now):
    if len(tokens) < 2:
        return False
    channel.botPart(tokens[1].lower(), send.whisper(nick))
    return True

def commandEmptyAll(db, nick, message, tokens, permissions, now):
    channel.botEmptyAll(send.whisper(nick))
    return True

def commandEmpty(db, nick, message, tokens, permissions, now):
    if len(tokens) < 2:
        return False
    channel.botEmpty(tokens[1].lower(), send.whisper(nick))
    return True

def commandManageBot(db, nick, message, tokens, permissions, now):
    if len(tokens) < 2:
        return False
    
    return managebot.botManageBot(db, send.whisper(nick), nick, message,
                                  tokens)
