from source.public.custom import broadcaster, countdown, multiple, params
from source.public.custom import query, url, user

fields = [broadcaster.fieldBroadcaster,
          user.fieldUser,
          query.fieldQuery,
          url.fieldUrl,
          countdown.fieldCountdown,
          countdown.fieldSince,
          countdown.fieldNext,
          countdown.fieldPrevious,
          ]
fieldsEnd = [params.fieldParams]
properties = ['multiple', 'delimiter']
postProcess = [multiple.propertyMultipleLines]
