import lists.feature
from typing import Set
from ...data import Send
from ...data.message import Message
from ...database import DatabaseMain

enable: Set[str] = {
    '',
    'enable',
    'yes',
    '1',
    }
disable: Set[str] = {
    'disable',
    'no',
    '0',
    }


async def feature(database: DatabaseMain,
                  channel: str,
                  message: Message,
                  send: Send) -> bool:
    action: str = message.lower[2] if len(message) >= 3 else ''

    feature_: str = message.lower[1]
    if (feature_ not in lists.feature.features
            or lists.feature.features[feature_] is None):
        send('Unrecognized feature: ' + feature_)
        return True

    if action in enable:
        return await feature_add(database, channel, feature_, send)
    if action in disable:
        return await feature_remove(database, channel, feature_, send)

    send('Unrecognized second parameter: ' + action)
    return True


async def feature_add(database: DatabaseMain,
                      channel: str,
                      feature_: str,
                      send: Send) -> bool:
    hasFeature: bool = await database.hasFeature(channel, feature_)
    if not hasFeature:
        await database.addFeature(channel, feature_)

    msg: str
    if hasFeature:
        msg = 'The feature {feature} has already been enabled in {channel}'
    else:
        msg = 'The feature {feature} has been enabled in {channel}'
    send(msg.format(feature=lists.feature.features[feature_], channel=channel))
    return True


async def feature_remove(database: DatabaseMain,
                         channel: str,
                         feature_: str,
                         send: Send) -> bool:
    hasFeature: bool = await database.hasFeature(channel, feature_)
    if hasFeature:
        await database.removeFeature(channel, feature_)

    msg: str
    if hasFeature:
        msg = 'The feature {feature} has been disabled in {channel}'
    else:
        msg = 'The feature {feature} was not enabled in {channel}'
    send(msg.format(feature=lists.feature.features[feature_], channel=channel))
    return True
