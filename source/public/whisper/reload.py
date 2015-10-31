from ..common import reload
from bot import globals

def sendMessage(nick):
    return lambda m, p=1: globals.messaging.queueWhisper(nick, m, p)

def commandReload(db, nick, message, msgParts, permissions):
    reload.botReload(sendMessage(nick), nick, message, msgParts, permissions)
    return True

def commandReloadCommands(db, nick, message, msgParts, permissions):
    reload.botReloadCommands(sendMessage(nick), nick, message, msgParts,
                             permissions)
    return True

def commandReloadConfig(db, nick, message, msgParts, permissions):
    reload.botReloadConfig(sendMessage(nick), nick, message, msgParts,
                           permissions)
    return True
