from ..common import feature
from bot import globals

def sendMessage(nick):
    return lambda m, p=1: globals.messaging.queueWhisper(nick, m, p)

def commandFeature(db, nick, message, msgParts, permissions):
    return feature.botFeature(db, nick, msgParts, sendMessage(nick))
