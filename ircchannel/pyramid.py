from config import config
import ircbot.irc
import random

def commandPyramid(channelThread, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    rep = msgParts[1] + ' '
    try:
        count = int(msgParts[2])
    except:
        count = 5
    count = min(count, (2048 - 11 - len(channelThread.channel)) // len(rep))
    for i in range(1, count + 1):
        channelThread.sendMessage(rep * i, 2)
    for i in range(count - 1, 0, -1):
        channelThread.sendMessage(rep * i, 2)
    return True

def commandRPyramid(channelThread, nick, message, msgParts, permissions):
    emotes = [
        'PogChamp', 'Kappa', 'Keepo', 'DansGame', 'SwiftRage', 'PJSalt',
        'OpieOP', 'PogChamp', 'Kreygasm', 'BibleThump', 'SoBayed', 'KAPOW',
        'ResidentSleeper', 'FrankerZ', 'KevinTurtle', 'HumbleLife',
        'BrainSlug', 'BloodTrail', 'panicBasket', 'WinWaker', 'TriHard',
        'OneHand', 'NightBat', 'MrDestructoid', 'Kippa', 'RalpherZ', 
        ':)', ':(', ':o', ':z', 'B)', ':/', ';)', ';p', ':p', 'R)', 'o_O',
        ':D', '>(', '<3',
        ]
    try:
        count = int(msgParts[1])
    except:
        count = 5
    rep = []
    for i in range(count):
        rep.append(emotes[random.randrange(len(emotes))])
        if len(' '.join(rep)) >= (2048 - 11 - len(channelThread.channel)):
            del rep[-1]
            break
    for i in range(1, count + 1):
        channelThread.sendMessage(' '.join(rep[0:i]), 2)
    for i in range(count - 1, 0, -1):
        channelThread.sendMessage(' '.join(rep[0:i]), 2)
    return True

def commandPyramidLong(channelThread, nick, message, msgParts, permissions):
    msgParts = message.split(None, 1)
    rep = msgParts[1] + ' '
    try:
        count = int(msgParts[0].split('-')[1])
    except:
        count = 5
    count = min(count, (2048 - 11 - len(channelThread.channel)) // len(rep))
    for i in range(1, count + 1):
        channelThread.sendMessage(rep * i, 2)
    for i in range(count - 1, 0, -1):
        channelThread.sendMessage(rep * i, 2)
    return True
