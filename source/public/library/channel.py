from bot import config, globals, utils
from typing import Dict, List, Optional, Union
from . import timeout
from ...api import twitch
from ...data import Send
from ...database import DatabaseBase


def join(database: DatabaseBase,
         channel: str,
         send: Send) -> bool:
    if database.isChannelBannedReason(channel):
        send('Chat ' + channel + ' is banned from joining')
        return True
    priority = database.getAutoJoinsPriority(channel)  # type: Union[int, float]

    cluster = twitch.chat_server(channel)  # type: Optional[str]
    if cluster not in globals.clusters:
        send('Unknown chat server for ' + channel)
    elif utils.joinChannel(channel, priority, cluster):
        send('Joining ' + channel)
    else:
        result = utils.ensureServer(channel, priority, cluster)  # type: int
        if result == utils.ENSURE_CORRECT:
            send('Already joined ' + channel)
        elif result == utils.ENSURE_REJOIN:
            send('Moved ' + channel + ' to correct chat server')
        else:
            send('Unknown error joining ' + channel)
    return True


def part(channel: str,
         send: Send) -> bool:
    if channel == config.botnick:
        return False
    utils.partChannel(channel)
    send('Leaving ' + channel)
    return True


def say(database: DatabaseBase,
        nick: str,
        channel: str,
        message: str) -> bool:
    if channel in globals.channels:
        timeout.record_timeout(
            database, globals.channels[channel], nick, message, None, 'say')
        globals.channels[channel].send(message)
        return True
    return False


def empty_all(send: Send) -> bool:
    utils.clearAllChat()
    send('Cleared all queued messages')
    return True


def empty(channel: str,
          send: Send) -> bool:
    if channel in globals.channels:
        chan = globals.channels[channel]
        chan.clear()
        send('Cleared all queued messages for ' + channel)
        return True
    return False
