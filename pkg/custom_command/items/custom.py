from lib import data
from ..custom import broadcaster, countdown, multiple, params
from ..custom import query, url, user
from typing import Collection, Iterable


def fields() -> Iterable[data.CustomCommandField]:
    yield broadcaster.fieldBroadcaster
    yield user.fieldUser
    yield query.fieldQuery
    yield url.fieldUrl
    yield countdown.fieldCountdown
    yield countdown.fieldSince
    yield countdown.fieldNext
    yield countdown.fieldPrevious
    yield params.fieldParams


def properties() -> Collection[str]:
    if not hasattr(properties, 'properties'):
        setattr(properties, 'properties', ['multiple', 'delimiter'])
    return getattr(properties, 'properties')


def postProcess() -> Iterable[data.CustomCommandProcess]:
    yield multiple.propertyMultipleLines
