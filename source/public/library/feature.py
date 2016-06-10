from lists.feature import features
from typing import Set
from ...data.argument import Send
from ...data.message import Message
from ...database.databasebase import DatabaseBase

enable = {
    '',
    'enable',
    'yes',
    '1',
    }  # type: Set[str]
disable = {
    'disable',
    'no',
    '0',
    }  # type: Set[str]


def botFeature(database: DatabaseBase,
               channel: str,
               message: Message,
               send: Send) -> bool:
    if len(message) < 2:
        return False
    
    action = ''  # type: str
    if len(message) >= 3:
        action = message.lower[2]
    
    if message.lower[1] not in features or features[message.lower[1]] is None:
        send('Unrecognized feature: ' + message.lower[1])
        return True
    
    if action not in enable and action not in disable:
        msg = 'Unrecognized second parameter: ' + action  # type: str
        send(msg)
        return True
    
    hasFeature = database.hasFeature(channel, message.lower[1])  # type: bool
    if not hasFeature and action in enable:
        database.addFeature(channel, message.lower[1])
    if hasFeature and action in disable:
        database.removeFeature(channel, message.lower[1])
    
    msg = ''
    if hasFeature:
        if action in enable:
            msg = 'The feature {feature} has already been enabled in {channel}'
        if action in disable:
            msg = 'The feature {feature} has been disabled in {channel}'
    else:
        if action in enable:
            msg = 'The feature {feature} has been enabled in {channel}'
        if action in disable:
            msg = 'The feature {feature} was not enabled in {channel}'
    send(msg.format(feature=features[message.lower[1]], channel=channel))
    return True
