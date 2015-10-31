from ..common import feature, send
from bot import globals

def commandFeature(db, nick, message, msgParts, permissions):
    return feature.botFeature(db, nick, msgParts, send.whisper(nick))
