from ..common import reload, send
from bot import globals

def commandReload(db, nick, message, msgParts, permissions, now):
    reload.botReload(send.whisper(nick))
    return True

def commandReloadCommands(db, nick, message, msgParts, permissions, now):
    reload.botReloadCommands(send.whisper(nick))
    return True

def commandReloadConfig(db, nick, message, msgParts, permissions, now):
    reload.botReloadConfig(send.whisper(nick))
    return True
