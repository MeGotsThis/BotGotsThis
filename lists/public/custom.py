from source.public.custom import countdown, params, query, url, user
try:
    from ..private import custom as privateCustom
except:
    from ..private.default import custom as privateCustom

fields = [user.fieldUser,
          query.fieldQuery,
          url.fieldUrl,
          countdown.fieldCountdown,
          countdown.fieldSince,
          countdown.fieldNext,
          countdown.fieldPrevious,
          ]
fields += privateCustom.fields + [params.fieldParams]
