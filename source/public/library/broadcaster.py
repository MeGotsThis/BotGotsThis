import bot.config
import bot.globals
import time
from bot import utils
from typing import Dict, List, Optional, Union
from ...api import twitch
from ...data import Send
from ...data.message import Message
from ...database import DatabaseBase


def come(database: DatabaseBase,
         channel: str,
         send: Send) -> bool:
    if database.isChannelBannedReason(channel) is not None:
        send('Chat {channel} is banned from joining'.format(channel=channel))
        return True
    priority: Union[float, int] = database.getAutoJoinsPriority(channel)
    cluster: Optional[str] = twitch.chat_server(channel)
    joinResult: Optional[bool] = utils.joinChannel(channel, priority, cluster)
    if joinResult is None:
        send('Unable to join {channel} on a specified server according to '
             'twitch'.format(channel=channel))
    elif joinResult:
        send('Joining {channel}'.format(channel=channel))
    else:
        ensureResult: int = utils.ensureServer(channel, priority, cluster)
        if ensureResult == utils.ENSURE_CORRECT:
            send('I am already in {channel}'.format(channel=channel))
        elif ensureResult == utils.ENSURE_REJOIN:
            send('Moved {channel} to correct chat '
                 'server'.format(channel=channel))
        else:
            send('Unknown Error')
    return True


def leave(channel: str,
          send: Send) -> bool:
    if channel == bot.config.botnick:
        return False
    send('Bye {channel}'.format(channel=channel))
    time.sleep(1.0)
    utils.partChannel(channel)
    return True


def empty(channel: str,
          send: Send) -> bool:
    if channel in bot.globals.channels:
        chan = bot.globals.channels[channel]
        chan.clear()
        send('Cleared all queued messages '
             'for {channel}'.format(channel=channel))
    return True


def auto_join(database: DatabaseBase,
              channel: str,
              send: Send,
              message: Message) -> bool:
    if database.isChannelBannedReason(channel) is not None:
        send('Chat {channel} is banned from '
             'joining'.format(channel=channel))
        return True

    if len(message) >= 2:
        removeMsgs: List[str] = ['0', 'false', 'no', 'remove', 'rem', 'delete',
                                 'del', 'leave', 'part']
        if message.lower[1] in removeMsgs:
            return auto_join_delete(database, channel, send)
    return auto_join_add(database, channel, send)


def auto_join_add(database: DatabaseBase,
                  channel: str,
                  send: Send) -> bool:
    cluster: Optional[str] = twitch.chat_server(channel)
    if cluster is None:
        send('Auto join for {channel} failed due to Twitch '
             'error'.format(channel=channel))
        return True
    if cluster not in bot.globals.clusters:
        send('Auto join for {channel} failed due to unsupported chat '
             'server'.format(channel=channel))
        return True
    result: bool = database.saveAutoJoin(channel, 0, cluster)
    priority: Union[int, float] = database.getAutoJoinsPriority(channel)
    if result is False:
        database.setAutoJoinServer(channel, cluster)

    wasInChat: bool = not utils.joinChannel(channel, priority, cluster)
    rejoin: int = 0
    if wasInChat:
        rejoin = utils.ensureServer(channel, priority, cluster)

    msg: str
    if result and not wasInChat:
        msg = ('Auto join for {channel} is now enabled and joined {channel} '
               'chat')
    elif result:
        if rejoin < 0:
            msg = ('Auto join for {channel} is now enabled and moved to the '
                   'correct server')
        else:
            msg = 'Auto join for {channel} is now enabled'
    elif not wasInChat:
        msg = ('Auto join for {channel} is already enabled but now joined '
               '{channel} chat')
    else:
        if rejoin < 0:
            msg = ('Auto join for {channel} is already enabled and moved to '
                   'the correct server')
        else:
            msg = ('Auto join for {channel} is already enabled and already '
                   'in chat')
    send(msg.format(channel=channel))
    return True


def auto_join_delete(database: DatabaseBase,
                     channel: str,
                     send: Send) -> bool:
    result: bool = database.discardAutoJoin(channel)
    if result:
        send('Auto join for {channel} is now disabled'.format(channel=channel))
    else:
        send('Auto join for {channel} was never '
             'enabled'.format(channel=channel))
    return True


def set_timeout_level(database: DatabaseBase,
                      channel: str,
                      send: Send,
                      message: Message) -> bool:
    propertyDict: Dict[str, str] = {
        '1': 'timeoutLength0',
        '2': 'timeoutLength1',
        '3': 'timeoutLength2',
        }
    ordinal: Dict[str, str] = {
        '1': '1st',
        '2': '2nd',
        '3': '3rd',
        }
    k: str = message.command.split('settimeoutlevel-')[1]
    if k not in propertyDict:
        return False
    value: Optional[int]
    try:
        value = int(message[1])
    except (ValueError, IndexError):
        value = None
    timeout: int = bot.config.moderatorDefaultTimeout[int(k) - 1]
    default: str = '{} seconds'.format(timeout) if timeout else 'Banned'
    saveValue: Optional[str] = str(value) if value is not None else None
    database.setChatProperty(channel, propertyDict[k], saveValue)
    msg: str
    if value is None:
        msg = ('Setting the timeout length for {ordinal} offense to defaulted '
               'amount ({default})')
    elif value:
        msg = ('Setting the timeout length for {ordinal} offense to {value} '
               'seconds')
    else:
        msg = 'Setting the timeout length for {ordinal} offense to banning'
    send(msg.format(ordinal=ordinal[k], default=default, value=value))
    return True
