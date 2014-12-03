from . import statExpTable
from config import config
import ircbot.irc
import os.path
import math
import re

nidoranMBase = {
    'hp': 46,
    'attack': 57,
    'defense': 40,
    'speed': 50,
    'special': 40,
}
nidorinoBase = {
    'hp': 61,
    'attack': 72,
    'defense': 57,
    'speed': 65,
    'special': 55,
}
nidokingBase = {
    'hp': 81,
    'attack': 92,
    'defense': 77,
    'speed': 85,
    'special': 75,
}

nidoranStats = {}

def commandNidoranRed(channelData, nick, message, msgParts, permissions):
    channel = channelData.channel
    if (channel not in nidoranStats or
        (len(msgParts) >= 2 and msgParts[1] == 'reset')):
        resetNidoran(channel)
        if len(msgParts) >= 2 and msgParts[1] == 'reset':
            return True
    if permissions['owner'] and len(msgParts) >= 2:
        if msgParts[1] == 'log':
            if channel in nidoranStats:
                channelData.sendMessage(repr(nidoranStats[channel]))
            return True
        if msgParts[1] == 'print':
            if channel in nidoranStats:
                if config.ircLogFolder:
                    fileName = channelData.channel + '.log'
                    pathArgs = config.ircLogFolder, fileName
                    with open(os.path.join(*pathArgs), 'a',
                              encoding='utf-8') as file:
                        file.write(repr(nidoranStats[channel]) + '\n')
                print(channel, repr(nidoranStats[channel]))
            return True
    if len(msgParts) >= 2 and msgParts[1] == 'stats':
        try:
            level = int(msgParts[2])
        except:
            level = None
        
        if level is not None:
            channelData.sendMessage(printStatsLevel(channel, level))
            return True
        
        return False
    
    pattern = r"^!nidoran\s+(\d{1,3})\s+((\d{1,3})\s+|\D+)?"
    pattern += r"(.+)[/\\\-](.+)[/\\\-](.+)[/\\\-](.+)"
    result = re.match(pattern, message)
    if result is not None:
        level = int(result.group(1))
        try:
            hp = int(result.group(3))
        except:
            hp = None
        try:
            attack = int(result.group(4))
        except:
            attack = None
        try:
            defense = int(result.group(5))
        except:
            defense = None
        try:
            speed = int(result.group(6))
        except:
            speed = None
        try:
            special = int(result.group(7))
        except:
            special = None
        processStats(channel, level, hp, attack, defense, speed, special,
                     message)
    return False

def commandDvs(channelData, nick, message, msgParts, permissions):
    channelData.sendMessage(printNidoran(channelData.channel))

def printNidoran(channel):
    if (channel not in nidoranStats or
        nidoranStats[channel]['currentLevel'] is None):
        return 'No stats were set'
    
    dvs = nidoranStats[channel]['dvs']
    if (len(dvs['hp']) == 0 or len(dvs['attack']) == 0 or
        len(dvs['defense']) == 0 or len(dvs['speed']) == 0 or
        len(dvs['special']) == 0):
        badStat = []
        if len(dvs['hp']) == 0:
            badStat.append('HP')
        if len(dvs['attack']) == 0:
            badStat.append('Attack')
        if len(dvs['defense']) == 0:
            badStat.append('Defense')
        if len(dvs['speed']) == 0:
            badStat.append('Speed')
        if len(dvs['special']) == 0:
            badStat.append('Special')
        
        rtn = 'Invalid stats were set, could not compute: '
        rtn += ', '.join(badStat)
        return rtn
    
    verb = 'could be'
    if (len(dvs['hp']) == 1 and len(dvs['attack']) == 1 and
        len(dvs['defense']) == 1 and len(dvs['speed']) == 1 and
        len(dvs['special']) == 1):
        verb = 'are'
    
    return ('DVs ' + verb + 
            ' HP: ' + ', '.join([str(i) for i in dvs['hp']]) +
            '; Attack: ' + ', '.join([str(i) for i in dvs['attack']]) +
            '; Defense: ' + ', '.join([str(i) for i in dvs['defense']]) +
            '; Speed: ' + ', '.join([str(i) for i in dvs['speed']]) +
            '; Special: ' + ', '.join([str(i) for i in dvs['special']]))

def resetNidoran(channel):
    stats = {}
    stats['currentLevel'] = None
    stats['stats'] = {
        #0: {
        #    'hp': 0,
        #    'attack': 0,
        #    'defense': 0,
        #    'speed': 0,
        #    'special': 0,
        #},
    }
    stats['commands'] = []
    stats['log'] = {
        #0: [{
        #    'hp': 0,
        #    'attack': 0,
        #    'defense': 0,
        #    'speed': 0,
        #    'special': 0,
        #}],
    }
    stats['dvs'] = {
        'hp': set(range(16)),
        'attack': set(range(16)),
        'defense': set(range(16)),
        'speed': set(range(16)),
        'special': set(range(16)),
    }
    nidoranStats[channel] = stats

def printStatsLevel(channel, level):
    base = nidokingBase
    statExpLevel = statExpTable.nidokingStatExpRange
    if level in statExpTable.nidorinoStatExpRange:
        base = nidorinoBase
        statExpLevel = statExpTable.nidorinoStatExpRange
    if level in statExpTable.nidoranStatExpRange:
        base = nidoranMBase
        statExpLevel = statExpTable.nidoranStatExpRange
    
    hp = []
    attack = []
    defense = []
    speed = []
    special = []
    
    for dv in range(16):
        hp.append(getHpStat(level, base['hp'], dv, statExpLevel[level]['hp']))
        attack.append(getStat(level, base['attack'], dv,
                      statExpLevel[level]['attack']))
        defense.append(getStat(level, base['defense'], dv,
                       statExpLevel[level]['defense']))
        speed.append(getStat(level, base['speed'], dv,
                     statExpLevel[level]['speed']))
        special.append(getStat(level, base['special'], dv,
                       statExpLevel[level]['special']))
    
    rtn = ''
    rtn += 'HP: ' + printStatList(hp) + ', '
    rtn += 'Attack: ' + printStatList(attack) + ', '
    rtn += 'Defense: ' + printStatList(defense) + ', '
    rtn += 'Speed: ' + printStatList(speed) + ', '
    rtn += 'Special: ' + printStatList(special)
    return rtn

def printStatList(theList):
    prevStat = None
    statDvs = {}
    for dv, stat in enumerate(theList):
        if stat not in statDvs:
            statDvs[stat] = []
        statDvs[stat].append(dv)
    rtn = ''
    for stat, dvs in statDvs.items():
        if rtn:
            rtn += ', '
        if len(dvs) == 1:
            rtn += str(stat) + ': DV ' + str(dvs[0])
        else:
            rtn += str(stat) + ': DV ' + str(min(dvs)) + ' to ' + str(max(dvs))
    return rtn

def processStats(channel, level, hp=None, attack=None, defense=None,
                 speed=None, special=None, message=None, log=True):
    if (nidoranStats[channel]['currentLevel'] is not None and
        nidoranStats[channel]['currentLevel'] > level):
        return False
    
    if level not in nidoranStats[channel]['log']:
        nidoranStats[channel]['log'][level] = []
    if log:
        nidoranStats[channel]['commands'].append(message)
        nidoranStats[channel]['log'][level].append({
            'hp': hp,
            'attack': attack,
            'defense': defense,
            'speed': speed,
            'special': special,
        })
    
    base = nidokingBase
    statExpLevel = statExpTable.nidokingStatExpRange
    if level in statExpTable.nidorinoStatExpRange:
        base = nidorinoBase
        statExpLevel = statExpTable.nidorinoStatExpRange
    if level in statExpTable.nidoranStatExpRange:
        base = nidoranMBase
        statExpLevel = statExpTable.nidoranStatExpRange
    
    nidoranStats[channel]['currentLevel'] = level
    
    if (len(nidoranStats[channel]['dvs']['hp']) == 1 and
        len(nidoranStats[channel]['dvs']['attack']) == 1 and
        len(nidoranStats[channel]['dvs']['defense']) == 1 and
        len(nidoranStats[channel]['dvs']['speed']) == 1 and
        len(nidoranStats[channel]['dvs']['special']) == 1):
        return
    
    if hp is not None:
        for dv in nidoranStats[channel]['dvs']['hp'].copy():
            if getHpStat(level, base['hp'], dv,
                         statExpLevel[level]['hp']) != hp:
                nidoranStats[channel]['dvs']['hp'].remove(dv)
        bit = checkBit(0x08, nidoranStats[channel]['dvs']['hp'])
        if bit is not None:
            for dv in nidoranStats[channel]['dvs']['attack'].copy():
                if bool(dv & 1) != bool(bit):
                    nidoranStats[channel]['dvs']['attack'].remove(dv)
        bit = checkBit(0x04, nidoranStats[channel]['dvs']['hp'])
        if bit is not None:
            for dv in nidoranStats[channel]['dvs']['defense'].copy():
                if bool(dv & 1) != bool(bit):
                    nidoranStats[channel]['dvs']['defense'].remove(dv)
        bit = checkBit(0x02, nidoranStats[channel]['dvs']['hp'])
        if bit is not None:
            for dv in nidoranStats[channel]['dvs']['speed'].copy():
                if bool(dv & 1) != bool(bit):
                    nidoranStats[channel]['dvs']['speed'].remove(dv)
        bit = checkBit(0x01, nidoranStats[channel]['dvs']['hp'])
        if bit is not None:
            for dv in nidoranStats[channel]['dvs']['special'].copy():
                if bool(dv & 1) != bool(bit):
                    nidoranStats[channel]['dvs']['special'].remove(dv)
    
    if level in statExpLevel:
        if attack is not None:
            for dv in nidoranStats[channel]['dvs']['attack'].copy():
                if getStat(level, base['attack'], dv,
                           statExpLevel[level]['attack']) != attack:
                    nidoranStats[channel]['dvs']['attack'].remove(dv)
        
        if defense is not None:
            for dv in nidoranStats[channel]['dvs']['defense'].copy():
                if getStat(level, base['defense'], dv,
                           statExpLevel[level]['defense']) != defense:
                    nidoranStats[channel]['dvs']['defense'].remove(dv)
        
        if speed is not None:
            for dv in nidoranStats[channel]['dvs']['speed'].copy():
                if getStat(level, base['speed'], dv,
                           statExpLevel[level]['speed']) != speed:
                    nidoranStats[channel]['dvs']['speed'].remove(dv)
        
        if special is not None:
            for dv in nidoranStats[channel]['dvs']['special'].copy():
                if getStat(level, base['special'], dv,
                           statExpLevel[level]['special']) != special:
                    nidoranStats[channel]['dvs']['special'].remove(dv)
    
    if (len(nidoranStats[channel]['dvs']['hp']) > 1 and
        len(nidoranStats[channel]['dvs']['attack']) == 1 and
        len(nidoranStats[channel]['dvs']['defense']) == 1 and
        len(nidoranStats[channel]['dvs']['speed']) == 1 and
        len(nidoranStats[channel]['dvs']['special']) == 1):
        nidoranStats[channel]['dvs']['hp'] = {
            ((list(nidoranStats[channel]['dvs']['attack'])[0] & 1) << 3) |
            ((list(nidoranStats[channel]['dvs']['defense'])[0] & 1) << 2) |
            ((list(nidoranStats[channel]['dvs']['speed'])[0] & 1) << 1) |
            ((list(nidoranStats[channel]['dvs']['special'])[0] & 1) << 0)
        }

def getStat(level, baseStat, dv, statExp):
    num = int(2 * baseStat + 2 * dv + math.ceil(math.sqrt(statExp)) / 4)
    return int(num * level / 100) + 5

def getHpStat(level, baseStat, dv, statExp):
    num = int(2 * baseStat + 2 * dv + math.ceil(math.sqrt(statExp)) / 4 + 100)
    return int(num * level / 100) + 10

def checkBit(bit, dvSet):
    match = None
    for dv in dvSet:
        if match is None:
            match = (dv & bit)
        if (dv & bit) != match:
            return None
    return match
    

pass
