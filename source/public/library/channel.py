from bot import config, globals, utils
from typing import Dict, List, Optional, Union
from . import timeout
from ...api import twitch
from ...data.argument import Send
from ...database.databasebase import DatabaseBase


def botJoin(database: DatabaseBase,
            channel: str,
            send: Send) -> bool:
    if database.isChannelBannedReason(channel):
        send('Chat ' + channel + ' is banned from joining')
        return True
    priority = database.getAutoJoinsPriority(channel)  # type: Union[int, float]

    cluster = twitch.twitchChatServer(channel) or 'aws'  # type: str
    if utils.joinChannel(channel, priority, cluster):
        send('Joining ' + channel)
    else:
        result = utils.ensureServer(channel, priority, cluster)  # type: int
        if result == utils.ENSURE_CORRECT:
            send('Already joined ' + channel)
        elif result == utils.ENSURE_REJOIN:
            send('Moved ' + channel + ' to correct chat server')
    return False


def botPart(channel: str,
            send: Send) -> None:
    if channel == config.botnick:
        return
    utils.partChannel(channel)
    send('Leaving ' + channel)


def botSay(database: DatabaseBase,
           nick: str,
           channel: str,
           message: str) -> None:
    if channel in globals.channels:
        timeout.recordTimeoutFromCommand(
            database, globals.channels[channel], nick, message, None, 'say')
        globals.channels[channel].send(message)


def botEmptyAll(send: Send) -> None:
    utils.clearAllChat()
    send('Cleared all queued messages')


def botEmpty(channel: str,
             send: Send) -> None:
    if channel in globals.channels:
        chan = globals.channels[channel]
        chan.socket.messaging.clearChat(chan)
        send('Cleared all queued messages for ' + channel)
