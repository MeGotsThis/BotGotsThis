from .public import custom as publicCustom
try:
    from .private import custom as privateCustom
except:
    from .private.default import custom as privateCustom

fields = []
if not privateCustom.disablePublic:
    fields = privateCustom.fields
else:
    fields = publicCustom.fields + privateCustom.fields
    fields += publicCustom.fieldsEnd
