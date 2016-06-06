from source.data.argument import CustomFieldArgs, CustomProcessArgs
from source.public.custom import broadcaster, countdown, multiple, params
from source.public.custom import query, url, user
from typing import Callable, List, Optional

fields = [broadcaster.fieldBroadcaster,
          user.fieldUser,
          query.fieldQuery,
          url.fieldUrl,
          countdown.fieldCountdown,
          countdown.fieldSince,
          countdown.fieldNext,
          countdown.fieldPrevious,
          ]  # type: List[Callable[[CustomFieldArgs], Optional[str]]]
fieldsEnd = [params.fieldParams]  # type: List[Callable[[CustomFieldArgs], Optional[str]]]
properties = ['multiple', 'delimiter']  # type: List[str]
postProcess = [multiple.propertyMultipleLines]  # type: List[Callable[[CustomProcessArgs], Optional[str]]]
