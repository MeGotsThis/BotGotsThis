from config import config
import ircbot.channeldata
import ircbot.ircsocket
import ircbot.message
import ircbot.join

# Import some necessary libraries.
messaging = ircbot.message.MessageQueue()
mainChat = ircbot.ircsocket.SocketThread(config.mainServer, name='Main Chat')
eventChat = ircbot.ircsocket.SocketThread(config.eventServer, name='Event Chat')
join = ircbot.join.JoinThread()
join.add(mainChat)
join.add(eventChat)
channels = {}

def joinChannel(channel, priority=float('inf'), eventServer=False):
    if channel[0] != '#':
        channel = '#' + channel
    channel = channel.lower()
    if channel in channels:
        channels[channel].joinPriority = min(
            channels[channel].joinPriority, priority)
        return False
    socket = mainChat if not eventServer else eventChat
    params = channel, socket, priority
    channels[channel] = ircbot.channeldata.ChannelData(*params)
    socket.joinChannel(channels[channel])
    return True

def partChannel(channel):
    if channel[0] != '#':
        channel = '#' + channel
    if channel in channels:
        channels[channel].part()
        del channels[channel]

ENSURE_REJOIN_TO_MAIN = -2
ENSURE_REJOIN_TO_EVENT = -1
ENSURE_CORRECT = 0
ENSURE_NOT_JOINED = 1

def ensureServer(channel, priority=float('inf'), eventServer=False):
    if channel[0] != '#':
        channel = '#' + channel
    if channel not in channels:
        return ENSURE_NOT_JOINED
    socket = mainChat if not eventServer else eventChat
    if socket is channels[channel].socket:
        channels[channel].joinPriority = min(
            channels[channel].joinPriority, priority)
        return ENSURE_CORRECT
    partChannel(channel)
    joinChannel(channel, priority, eventServer)
    return ENSURE_REJOIN_TO_EVENT if eventServer else ENSURE_REJOIN_TO_MAIN

