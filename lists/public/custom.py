from source import data
from source.public.custom import broadcaster, countdown, multiple, params
from source.public.custom import query, url, user
from typing import List


def fields() -> List[data.CustomCommandField]:
    if not hasattr(fields, 'fields'):
        setattr(fields, 'fields', [
            broadcaster.fieldBroadcaster,
            user.fieldUser,
            query.fieldQuery,
            url.fieldUrl,
            countdown.fieldCountdown,
            countdown.fieldSince,
            countdown.fieldNext,
            countdown.fieldPrevious,
            ])
    return getattr(fields, 'fields')


def fieldsEnd() -> List[data.CustomCommandField]:
    if not hasattr(fieldsEnd, 'fields'):
        setattr(fieldsEnd, 'fields', [params.fieldParams])
    return getattr(fieldsEnd, 'fields')


def properties() -> List[str]:
    if not hasattr(properties, 'properties'):
        setattr(properties, 'properties', ['multiple', 'delimiter'])
    return getattr(properties, 'properties')


def postProcess() -> List[data.CustomCommandProcess]:
    if not hasattr(postProcess, 'post'):
        setattr(postProcess, 'post', [multiple.propertyMultipleLines])
    return getattr(postProcess, 'post')
