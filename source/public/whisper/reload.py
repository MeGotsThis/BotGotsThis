from ..library import reload, send
from bot import globals

def commandReload(db, nick, message, permissions, now):
    reload.botReload(send.whisper(nick))
    return True

def commandReloadCommands(db, nick, message, permissions, now):
    reload.botReloadCommands(send.whisper(nick))
    return True

def commandReloadConfig(db, nick, message, permissions, now):
    reload.botReloadConfig(send.whisper(nick))
    return True
