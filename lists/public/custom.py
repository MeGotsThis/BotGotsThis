from source.public.custom import countdown, params, query, url, user

fields = [user.fieldUser,
          query.fieldQuery,
          url.fieldUrl,
          countdown.fieldCountdown,
          countdown.fieldSince,
          countdown.fieldNext,
          countdown.fieldPrevious,
          ]
fieldsEnd = [params.fieldParams]
