from typing import Mapping, Optional, Set  # noqa: F401

import lib.items.feature
from lib.data import Send
from lib.data.message import Message
from lib.database import DatabaseMain

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
    features: Mapping[str, Optional[str]] = lib.items.feature.features()
    if feature_ not in features or features[feature_] is None:
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

    theFeature: str = lib.items.feature.features()[feature_]
    msg: str
    if hasFeature:
        send(f'The feature {theFeature} has already been enabled in {channel}')
    else:
        send(f'The feature {theFeature} has been enabled in {channel}')
    return True


async def feature_remove(database: DatabaseMain,
                         channel: str,
                         feature_: str,
                         send: Send) -> bool:
    hasFeature: bool = await database.hasFeature(channel, feature_)
    if hasFeature:
        await database.removeFeature(channel, feature_)

    theFeature: str = lib.items.feature.features()[feature_]
    msg: str
    if hasFeature:
        send(f'The feature {theFeature} has been disabled in {channel}')
    else:
        send(f'The feature {theFeature} was not enabled in {channel}')
    return True
