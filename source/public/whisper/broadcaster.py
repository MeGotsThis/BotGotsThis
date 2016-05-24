from ..library import broadcaster, send
from bot import globals

def commandCome(db, nick, message, permissions, now):
    broadcaster.botCome(db, nick, send.whisper(nick))
    return True

def commandLeave(db, nick, message, permissions, now):
    return broadcaster.botLeave(nick, send.whisper(nick))

def commandEmpty(db, nick, message, permissions, now):
    broadcaster.botEmpty(nick, send.whisper(nick))
    return True

def commandAutoJoin(db, nick, message, permissions, now):
    broadcaster.botAutoJoin(db, nick, send.whisper(nick), message)
    return True

