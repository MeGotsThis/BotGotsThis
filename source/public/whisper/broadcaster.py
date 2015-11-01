from ..common import broadcaster, send
from bot import globals

def commandCome(db, nick, message, msgParts, permissions):
    broadcaster.botCome(db, nick, send.whisper(nick))
    return True

def commandLeave(db, nick, message, msgParts, permissions):
    return broadcaster.botLeave(nick, send.whisper(nick))

def commandEmpty(db, nick, message, msgParts, permissions):
    broadcaster.botEmpty(nick, send.whisper(nick))
    return True

def commandAutoJoin(db, nick, message, msgParts, permissions):
    broadcaster.botAutoJoin(nick, send.whisper(nick), msgParts)
    return True

