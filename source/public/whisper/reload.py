from ..common import reload, send
from bot import globals

def commandReload(db, nick, message, msgParts, permissions):
    reload.botReload(send.whisper(nick), nick, message, msgParts, permissions)
    return True

def commandReloadCommands(db, nick, message, msgParts, permissions):
    reload.botReloadCommands(send.whisper(nick), nick, message, msgParts,
                             permissions)
    return True

def commandReloadConfig(db, nick, message, msgParts, permissions):
    reload.botReloadConfig(send.whisper(nick), nick, message, msgParts,
                           permissions)
    return True
