from ..common import broadcaster
from bot import globals

def sendMessage(nick):
    return lambda m, p=1: globals.messaging.queueWhisper(nick, m, p)

def commandCome(nick, message, msgParts, permissions):
    broadcaster.botCome(nick, sendMessage(nick))
    return True

def commandLeave(nick, message, msgParts, permissions):
    return broadcaster.botLeave(nick, sendMessage(nick))

def commandEmpty(nick, message, msgParts, permissions):
    broadcaster.botEmpty(nick, sendMessage(nick))
    return True

def commandAutoJoin(nick, message, msgParts, permissions):
    broadcaster.botAutoJoin(nick, sendMessage(nick), msgParts)
    return True

