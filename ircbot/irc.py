from config import config
import ircbot.channeldata
import ircbot.ircsocket
import ircbot.message
import ircbot.join
import datetime

# Import some necessary libraries.
messaging = ircbot.message.MessageQueue(name='Message Queue')
mainChat = ircbot.ircsocket.SocketThread(config.mainServer,
                                         name='Main Chat')
eventChat = ircbot.ircsocket.SocketThread(config.eventServer,
                                          name='Event Chat')
groupChat = ircbot.ircsocket.SocketThread(config.groupServer,
                                          name='Group Chat')
join = ircbot.join.JoinThread(name='Join Thread')
join.add(mainChat)
join.add(eventChat)
channels = {}
displayName = config.botnick
isTwitchTurbo = False
isTwitchAdmin = False
isTwitchStaff = False
emoteset = [0]
globalEmotes = {
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
    10: ':\\',
    11: ';)',
    13: ';P',
    12: ':P',
    14: 'R)',
    6: 'o_O',
    3: ':D',
    4: '>(',
    9: '<3',
    }
globalEmotesCache = datetime.datetime.min
globalSessionData = {}

def joinChannel(channel, priority=float('inf'), server=mainChat):
    if channel[0] != '#':
        channel = '#' + channel
    channel = channel.lower()
    if channel in channels:
        channels[channel].joinPriority = min(
            channels[channel].joinPriority, priority)
        return False
    params = channel, server, priority
    channels[channel] = ircbot.channeldata.ChannelData(*params)
    server.joinChannel(channels[channel])
    return True

def partChannel(channel):
    if channel[0] != '#':
        channel = '#' + channel
    if channel in channels:
        channels[channel].part()
        del channels[channel]

ENSURE_REJOIN_TO_MAIN = int(-2)
ENSURE_REJOIN_TO_EVENT = int(-1)
ENSURE_CORRECT = int(0)
ENSURE_NOT_JOINED = int(1)

def ensureServer(channel, priority=float('inf'), server=mainChat):
    if channel[0] != '#':
        channel = '#' + channel
    if channel not in channels:
        return ENSURE_NOT_JOINED
    if server is channels[channel].socket:
        channels[channel].joinPriority = min(
            channels[channel].joinPriority, priority)
        return ENSURE_CORRECT
    partChannel(channel)
    joinChannel(channel, priority, server)
    if server is eventChat:
        return ENSURE_REJOIN_TO_EVENT
    else:
        return ENSURE_REJOIN_TO_MAIN
