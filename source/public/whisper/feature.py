from ..library import feature, send
from bot import globals

def commandFeature(db, nick, message, permissions, now):
    return feature.botFeature(db, nick, message, send.whisper(nick))
