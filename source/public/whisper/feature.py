from ..common import feature
from bot import globals

def sendMessage(nick):
    return lambda m, p=1: globals.messaging.queueWhisper(nick, m, p)

def commandFeature(nick, message, msgParts, permissions):
    return feature.botFeature(nick, msgParts, sendMessage(nick))
