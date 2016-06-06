from bot import config, globals, utils
from . import timeout
from ...api import twitch


def botJoin(db, channel, send):
    if db.isChannelBannedReason(channel):
        send('Chat ' + channel + ' is banned from joining')
        return True
    priority = db.getAutoJoinsPriority(channel)
    priority = priority if priority is not None else float('inf')
    
    cluster = twitch.twitchChatServer(channel)
    if utils.joinChannel(channel, priority, cluster):
        send('Joining ' + channel)
    else:
        result = utils.ensureServer(channel, priority, cluster)
        if result == utils.ENSURE_CORRECT:
            send('Already joined ' + channel)
        elif result == utils.ENSURE_REJOIN:
            send('Moved ' + channel + ' to correct chat server')


def botPart(channel, send):
    if channel == config.botnick:
        return
    utils.partChannel(channel)
    send('Leaving ' + channel)


def botSay(db, nick, channel, message):
    if channel in globals.channels:
        timeout.recordTimeoutFromCommand(db, globals.channels[channel], nick,
                                         message, None, 'say')
        globals.channels[channel].send(message)


def botEmptyAll(send):
    utils.clearAllChat()
    send('Cleared all queued messages')


def botEmpty(channel, send):
    globals.channels[channel].socket.messaging.clearChat(channel)
    send('Cleared all queued messages for ' + channel)
