from .public import custom as publicCustom
try:
    from .private import custom as privateCustom
except ImportError:
    from .private.default import custom as privateCustom

fields = []
properties = []
postProcess = []
if privateCustom.disablePublic:
    fields = privateCustom.fields
    properties = privateCustom.properties
    postProcess = privateCustom.postProcess
else:
    fields = publicCustom.fields + privateCustom.fields
    fields += publicCustom.fieldsEnd
    properties = publicCustom.properties + privateCustom.properties
    postProcess = publicCustom.postProcess + privateCustom.postProcess
