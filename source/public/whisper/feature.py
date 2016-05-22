from ..common import feature, send
from bot import globals

def commandFeature(db, nick, message, tokens, permissions, now):
    return feature.botFeature(db, nick, tokens, send.whisper(nick))
