from config import config
import ircbot.irc
import random

def commandE(channelThread, nick, message, msgParts, permissions):
    raise Exception()
    pass

def commandX(channelThread, nick, message, msgParts, permissions):
    msgParts = message.split(None, 1)
    alpha = '0123456789'
    alpha += 'abcedefghijklmnopqrstuvwxyz'
    alpha += 'ABCDEFGFHIJKLMNOPQRSTUVWXYZ'
    alpha += '''`~!@#$%^&*()-_=+[]{}<>;:'"\/'''
    try:
        count = int(msgParts[1])
    except:
        count = 5
    rep = []
    for i in range(count):
        rep.append(alpha[random.randrange(len(alpha))])
    channelThread.sendMessage(''.join(rep))
    return True

def commandY(channelThread, nick, message, msgParts, permissions):
    msgParts = message.split(None, 2)
    alpha = '0123456789'
    alpha += 'abcedefghijklmnopqrstuvwxyz'
    alpha += 'ABCDEFGFHIJKLMNOPQRSTUVWXYZ'
    alpha += '''`~!@#$%^&*()-_=+[]{}<>;:'"\/'''
    try:
        if len(msgParts) == 2:
            repeat = 5
            length = int(msgParts[1])
        else:
            repeat = int(msgParts[1])
            length = int(msgParts[2])
    except:
        repeat = 5
        length = 5
    rep = list(alpha) * (length // len(alpha))
    subalpha = list(alpha)
    random.shuffle(subalpha)
    rep += subalpha[:length % len(alpha)]
    random.shuffle(rep)
    rep.append(' ')
    channelThread.sendMessage(''.join(rep) * repeat)
    return True
