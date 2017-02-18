from source import data
from source.public.custom import broadcaster, countdown, multiple, params
from source.public.custom import query, url, user
from typing import List

fields: List[data.CustomCommandField] = [
    broadcaster.fieldBroadcaster,
    user.fieldUser,
    query.fieldQuery,
    url.fieldUrl,
    countdown.fieldCountdown,
    countdown.fieldSince,
    countdown.fieldNext,
    countdown.fieldPrevious,
    ]
fieldsEnd: List[data.CustomCommandField] = [params.fieldParams]
properties: List[str] = ['multiple', 'delimiter']
postProcess: List[data.CustomCommandProcess] = [multiple.propertyMultipleLines]
