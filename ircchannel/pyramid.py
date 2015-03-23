from config import config
import ircbot.irc
import random

def commandPyramid(channelData, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    rep = msgParts[1] + ' '
    try:
        count = int(msgParts[2])
    except:
        count = 5
    count = min(count, (2048 - 11 - len(channelData.channel)) // len(rep))
    if not permissions['globalMod']:
        count = min(count, 20)
    messages = [rep * i for i in range(1, count)]
    messages += [rep * i for i in range(count, 0, -1)]
    channelData.sendMulipleMessages(messages, 2)
    return True

def commandRPyramid(channelData, nick, message, msgParts, permissions):
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
    if not permissions['globalMod']:
        count = min(count, 20)
    for i in range(count):
        rep.append(emotes[random.randrange(len(emotes))])
        if len(' '.join(rep)) >= (2048 - 11 - len(channelData.channel)):
            del rep[-1]
            break
    messages = [' '.join(rep[0:i]) for i in range(1, count)]
    messages += [' '.join(rep[0:i]) for i in range(count, 0, -1)]
    channelData.sendMulipleMessages(messages, 2)
    return True

def commandPyramidLong(channelData, nick, message, msgParts, permissions):
    msgParts = message.split(None, 1)
    if len(msgParts) < 2:
        return False
    rep = msgParts[1] + ' '
    try:
        count = int(msgParts[0].split('-')[1])
    except:
        count = 5
    count = min(count, (2048 - 11 - len(channelData.channel)) // len(rep))
    if not permissions['globalMod']:
        count = min(count, 20)
    messages = [rep * i for i in range(1, count)]
    messages += [rep * i for i in range(count, 0, -1)]
    channelData.sendMulipleMessages(messages, 2)
    return True
