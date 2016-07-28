import time
from bot import config, globals, utils
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
    priority = database.getAutoJoinsPriority(channel)  # type: Union[float, int]
    cluster = twitch.chat_server(channel)
    joinResult = utils.joinChannel(channel, priority, cluster)  # type: bool
    if joinResult is None:
        send('Unable to join {channel} on a specified server according to '
             'twitch'.format(channel=channel))
    elif joinResult:
        send('Joining {channel}'.format(channel=channel))
    else:
        ensureResult = utils.ensureServer(channel, priority, cluster)  # type: int
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
    if channel == config.botnick:
        return False
    send('Bye {channel}'.format(channel=channel))
    time.sleep(1)
    utils.partChannel(channel)
    return True


def empty(channel: str,
          send: Send) -> bool:
    if channel in globals.channels:
        chan = globals.channels[channel]
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
        removeMsgs = ['0', 'false', 'no', 'remove', 'rem', 'delete', 'del',
                      'leave', 'part']  # type: List[str]
        if message.lower[1] in removeMsgs:
            return auto_join_delete(database, channel, send)
    return auto_join_add(database, channel, send)


def auto_join_add(database: DatabaseBase,
                  channel: str,
                  send: Send) -> bool:
    cluster = twitch.chat_server(channel)  # type: str
    if cluster is None:
        send('Auto join for {channel} failed due to Twitch '
             'error'.format(channel=channel))
        return True
    if cluster not in globals.clusters:
        send('Auto join for {channel} failed due to unsupported chat '
             'server'.format(channel=channel))
        return True
    result = database.saveAutoJoin(channel, 0, cluster)
    priority = database.getAutoJoinsPriority(channel)  # type: Union[int, float]
    if result is False:
        database.setAutoJoinServer(channel, cluster)

    wasInChat = not utils.joinChannel(channel, priority, cluster)
    rejoin = 0  # type: int
    if wasInChat:
        rejoin = utils.ensureServer(channel, priority, cluster)

    if result and not wasInChat:
        msg = ('Auto join for {channel} is now enabled and joined {channel} '
               'chat')  # type: str
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
    result = database.discardAutoJoin(channel)  # type: bool
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
    propertyDict = {
        '1': 'timeoutLength0',
        '2': 'timeoutLength1',
        '3': 'timeoutLength2',
        }  # type: Dict[str, str]
    ordinal = {
        '1': '1st',
        '2': '2nd',
        '3': '3rd',
        }  # type: Dict[str, str]
    k = message.command.split('settimeoutlevel-')[1]  # type: str
    if k not in propertyDict:
        return False
    try:
        value = int(message[1])  # type: Optional[int]
    except (ValueError, IndexError):
        value = None
    timeout = config.moderatorDefaultTimeout[int(k) - 1]  # type: int
    default = '{} seconds'.format(timeout) if timeout else 'Banned'  # type: str
    saveValue = str(value) if value is not None else None  # type: Optional[str]
    database.setChatProperty(channel, propertyDict[k], saveValue)
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
