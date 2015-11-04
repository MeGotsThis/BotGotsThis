from source.public.custom import broadcaster, countdown, params, query, url
from source.public.custom import user

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
