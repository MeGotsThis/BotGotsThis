from typing import Mapping, Optional, Set  # noqa: F401

import lib.items.feature
from lib.cache import CacheStore
from lib.data import Send
from lib.data.message import Message
from lib.helper import parser


async def feature(data: CacheStore,
                  channel: str,
                  message: Message,
                  send: Send) -> bool:
    action: str = message.lower[2] if len(message) >= 3 else ''

    feature_: str = message.lower[1]
    features: Mapping[str, Optional[str]] = lib.items.feature.features()
    if feature_ not in features or features[feature_] is None:
        send('Unrecognized feature: ' + feature_)
        return True

    response: parser.Response = parser.get_response(action, default=parser.Yes)
    if response == parser.Yes:
        return await feature_add(data, channel, feature_, send)
    if response == parser.No:
        return await feature_remove(data, channel, feature_, send)

    send('Unrecognized second parameter: ' + action)
    return True


async def feature_add(data: CacheStore,
                      channel: str,
                      feature_: str,
                      send: Send) -> bool:
    hasFeature: bool = await data.hasFeature(channel, feature_)
    if not hasFeature:
        await data.addFeature(channel, feature_)

    theFeature: str = lib.items.feature.features()[feature_]
    msg: str
    if hasFeature:
        send(f'The feature {theFeature} has already been enabled in {channel}')
    else:
        send(f'The feature {theFeature} has been enabled in {channel}')
    return True


async def feature_remove(data: CacheStore,
                         channel: str,
                         feature_: str,
                         send: Send) -> bool:
    hasFeature: bool = await data.hasFeature(channel, feature_)
    if hasFeature:
        await data.removeFeature(channel, feature_)

    theFeature: str = lib.items.feature.features()[feature_]
    msg: str
    if hasFeature:
        send(f'The feature {theFeature} has been disabled in {channel}')
    else:
        send(f'The feature {theFeature} was not enabled in {channel}')
    return True
