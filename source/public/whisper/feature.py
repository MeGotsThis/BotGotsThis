from ..common import feature, send
from bot import globals

def commandFeature(db, nick, message, msgParts, permissions, now):
    return feature.botFeature(db, nick, msgParts, send.whisper(nick))
