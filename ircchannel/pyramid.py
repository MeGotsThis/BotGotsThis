from config import config
import database.factory
import ircbot.irc
import datetime
import random
import json

def commandPyramid(channelData, nick, message, msgParts, permissions):
    with database.factory.getDatabase() as db:
        if (not db.hasFeature(channelData.channel[1:], 'modpyramid') and
            not permissions['broadcaster']):
            return False
    if len(msgParts) < 2:
        return False
    rep = msgParts[1] + ' '
    try:
        count = int(msgParts[2])
    except:
        if permissions['broadcaster']:
            count = 5
        else:
            count = 3
    count = min(count, (2048 - 11 - len(channelData.channel)) // len(rep))
    if not permissions['broadcaster']:
        count = min(count, 5)
        
        currentTime = datetime.datetime.utcnow()
        cooldown = datetime.timedelta(seconds=config.spamModeratorCooldown)
        if 'modPyramid' in channelData.sessionData:
            since = currentTime - channelData.sessionData['modPyramid']
            if since < cooldown:
                return False
        channelData.sessionData['modPyramid'] = currentTime
    elif not permissions['globalMod']:
        count = min(count, 20)
    messages = [rep * i for i in range(1, count)]
    messages += [rep * i for i in range(count, 0, -1)]
    channelData.sendMulipleMessages(messages, 2)
    return True

def commandRPyramid(channelData, nick, message, msgParts, permissions):
    emotes = {
        25: 'Kappa',
        88: 'PogChamp',
        1902: 'Keepo',
        33: 'DansGame',
        34: 'SwiftRage',
        36: 'PJSalt',
        356: 'OpieOP',
        88: 'PogChamp',
        41: 'Kreygasm',
        86: 'BibleThump',
        1906: 'SoBayed',
        9803: 'KAPOW',
        245: 'ResidentSleeper',
        65: 'FrankerZ',
        40: 'KevinTurtle',
        27301: 'HumbleLife',
        881: 'BrainSlug',
        96: 'BloodTrail',
        22998: 'panicBasket',
        167: 'WinWaker',
        171: 'TriHard',
        66: 'OneHand',
        9805: 'NightBat',
        28: 'MrDestructoid',
        1901: 'Kippa',
        1900: 'RalpherZ', 
        1: ':)',
        2: ':(',
        8: ':o',
        5: ':z',
        7: 'B)',
        10: ':/',
        11: ';)',
        13: ';P',
        12: ':P',
        14: 'R)',
        6: 'o_O',
        3: ':D',
        4: '>(',
        9: '<3',
        }
    
    with database.factory.getDatabase() as db:
        if (not db.hasFeature(channelData.channel[1:], 'modpyramid') and
            not permissions['broadcaster']):
            return False
    
    currentTime = datetime.datetime.utcnow()
    if 'globalEmotes' in ircbot.irc.globalSessionData:
        emotes = ircbot.irc.globalSessionData['globalEmotes']
    
    cacheCooldown = datetime.timedelta(hours=1)
    needUpdate = 'globalEmotesCache' not in ircbot.irc.globalSessionData
    if 'globalEmotesCache' in ircbot.irc.globalSessionData:
        since = ircbot.irc.globalSessionData['globalEmotesCache'] - currentTime
        needUpdate = needUpdate or since > cacheCooldown
    if needUpdate:
        response, data = ircbot.twitchApi.twitchCall(
            None, 'GET', '/kraken/chat/emoticon_images?emotesets=0',
            headers = {
                'Accept': 'application/vnd.twitchtv.v3+json',
                })
        globalEmotes = json.loads(data.decode('utf-8'))['emoticon_sets']['0']
        emotes = {}
        replaceGlobal = {
            1: ':)',
            2: ':(',
            3: ':D',
            4: '>(',
            5: ':z',
            6: 'o_O',
            7: 'B)',
            8: ':o',
            9: '<3',
            10: ':/',
            11: ';)',
            12: ':P',
            13: ';P',
            14: 'R)',
            }
        for emote in globalEmotes:
            if emote['id'] in replaceGlobal:
                emotes[emote['id']] = replaceGlobal[emote['id']]
            else:
                emotes[emote['id']] = emote['code']
        ircbot.irc.globalSessionData['globalEmotes'] = emotes
        ircbot.irc.globalSessionData['globalEmotesCache'] = currentTime
    
    try:
        count = int(msgParts[1])
    except:
        if permissions['broadcaster']:
            count = 5
        else:
            count = 3
    rep = []
    if not permissions['broadcaster']:
        count = min(count, 5)
        
        currentTime = datetime.datetime.utcnow()
        cooldown = datetime.timedelta(seconds=config.spamModeratorCooldown)
        if 'modPyramid' in channelData.sessionData:
            since = currentTime - channelData.sessionData['modPyramid']
            if since < cooldown:
                return False
        channelData.sessionData['modPyramid'] = currentTime
    elif not permissions['globalMod']:
        count = min(count, 20)
    emoteIds = list(emotes.keys())
    for i in range(count):
        rep.append(emotes[random.choice(emoteIds)])
        if len(' '.join(rep)) >= (2048 - 11 - len(channelData.channel)):
            del rep[-1]
            break
    messages = [' '.join(rep[0:i]) for i in range(1, count)]
    messages += [' '.join(rep[0:i]) for i in range(count, 0, -1)]
    channelData.sendMulipleMessages(messages, 2)
    return True

def commandPyramidLong(channelData, nick, message, msgParts, permissions):
    with database.factory.getDatabase() as db:
        if (not db.hasFeature(channelData.channel[1:], 'modpyramid') and
            not permissions['broadcaster']):
            return False
    msgParts = message.split(None, 1)
    if len(msgParts) < 2:
        return False
    rep = msgParts[1] + ' '
    try:
        count = int(msgParts[0].split('-')[1])
    except:
        if permissions['broadcaster']:
            count = 5
        else:
            count = 3
    count = min(count, (2048 - 11 - len(channelData.channel)) // len(rep))
    if not permissions['broadcaster']:
        count = min(count, 5)
        
        currentTime = datetime.datetime.utcnow()
        cooldown = datetime.timedelta(seconds=config.spamModeratorCooldown)
        if 'modPyramid' in channelData.sessionData:
            since = currentTime - channelData.sessionData['modPyramid']
            if since < cooldown:
                return False
        channelData.sessionData['modPyramid'] = currentTime
    elif not permissions['globalMod']:
        count = min(count, 20)
    messages = [rep * i for i in range(1, count)]
    messages += [rep * i for i in range(count, 0, -1)]
    channelData.sendMulipleMessages(messages, 2)
    return True
