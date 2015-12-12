from ..common import broadcaster, send
from bot import globals

def commandCome(db, nick, message, msgParts, permissions, now):
    broadcaster.botCome(db, nick, send.whisper(nick))
    return True

def commandLeave(db, nick, message, msgParts, permissions, now):
    return broadcaster.botLeave(nick, send.whisper(nick))

def commandEmpty(db, nick, message, msgParts, permissions, now):
    broadcaster.botEmpty(nick, send.whisper(nick))
    return True

def commandAutoJoin(db, nick, message, msgParts, permissions, now):
    broadcaster.botAutoJoin(db, nick, send.whisper(nick), msgParts)
    return True

