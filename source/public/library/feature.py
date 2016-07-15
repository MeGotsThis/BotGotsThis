from lists.feature import features
from typing import Set
from ...data import Send
from ...data.message import Message
from ...database import DatabaseBase

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


def feature(database: DatabaseBase,
            channel: str,
            message: Message,
            send: Send) -> bool:
    action = message.lower[2] if len(message) >= 3 else ''  # type: str

    feature_ = message.lower[1]
    if feature_ not in features or features[feature_] is None:
        send('Unrecognized feature: ' + feature_)
        return True

    if action in enable:
        return feature_add(database, channel, feature_, send)
    if action in disable:
        return feature_remove(database, channel, feature_, send)

    msg = 'Unrecognized second parameter: ' + action  # type: str
    send(msg)
    return True


def feature_add(database: DatabaseBase,
                channel: str,
                feature_: str,
                send: Send) -> bool:
    hasFeature = database.hasFeature(channel, feature_)  # type: bool
    if not hasFeature:
        database.addFeature(channel, feature_)

    if hasFeature:
        msg = 'The feature {feature} has already been enabled in {channel}'  # type: str
    else:
        msg = 'The feature {feature} has been enabled in {channel}'
    send(msg.format(feature=features[feature_], channel=channel))
    return True


def feature_remove(database: DatabaseBase,
                   channel: str,
                   feature_: str,
                   send: Send) -> bool:
    hasFeature = database.hasFeature(channel, feature_)  # type: bool
    if hasFeature:
        database.removeFeature(channel, feature_)

    if hasFeature:
        msg = 'The feature {feature} has been disabled in {channel}'  # type: str
    else:
        msg = 'The feature {feature} was not enabled in {channel}'
    send(msg.format(feature=features[feature_], channel=channel))
    return True
