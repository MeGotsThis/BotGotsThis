from config import config
import ircbot.irc
import datetime

def commandWall(channelData, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
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
    length = min(length, (2048 - 11 - len(channelData.channel)) // len(rep))
    messages = [rep * length + ('' if i % 2 == 0 else ' ')
                for i in range(rows)]
    channelData.sendMulipleMessages(messages, 2)
    return True

def commandWallLong(channelData, nick, message, msgParts, permissions):
    msgParts = message.split(None, 1)
    if len(msgParts) < 2:
        return False
    try:
        rows = int(msgParts[0].split('-')[1])
    except:
        rows = 20
    messages = [msgParts[1] + ('' if i % 2 == 0 else ' ') for i in range(rows)]
    channelData.sendMulipleMessages(messages, 2)
    return True
