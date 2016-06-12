from source import data
from source.public.custom import broadcaster, countdown, multiple, params
from source.public.custom import query, url, user
from typing import List

fields = [broadcaster.fieldBroadcaster,
          user.fieldUser,
          query.fieldQuery,
          url.fieldUrl,
          countdown.fieldCountdown,
          countdown.fieldSince,
          countdown.fieldNext,
          countdown.fieldPrevious,
          ]  # type: List[data.CustomCommandField]
fieldsEnd = [params.fieldParams]  # type: List[data.CustomCommandField]
properties = ['multiple', 'delimiter']  # type: List[str]
postProcess = [multiple.propertyMultipleLines]  # type: List[data.CustomCommandProcess]
