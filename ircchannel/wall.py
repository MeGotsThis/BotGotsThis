from config import config
import ircbot.irc
import datetime

def commandWall(channelThread, nick, message, msgParts, permissions):
    rep = msgParts[1] + ' '
    try:
        if len(msgParts) == 3:
            length = 5
            rows = int(msgParts[2])
        else:
            length = int(msgParts[2])
            rows = int(msgParts[3])
    except:
        rows = 20
        length = 5
    length = min(length, (2048 - 11 - len(channelThread.channel)) // len(rep))
    for i in range(rows):
        if i % 2 == 0:
            channelThread.sendMessage(rep * length, 2)
        else:
            channelThread.sendMessage(rep * length + ' ', 2)
    return True

def commandWallLong(channelThread, nick, message, msgParts, permissions):
    msgParts = message.split(None, 1)
    try:
        rows = int(msgParts[0].split('-')[1])
    except:
        rows = 20
    for i in range(rows):
        if i % 2 == 0:
            channelThread.sendMessage(msgParts[1], 2)
        else:
            channelThread.sendMessage(msgParts[1] + ' ', 2)
    return True
