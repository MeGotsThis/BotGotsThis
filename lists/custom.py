from source import data
from typing import List
from .public import custom as publicCustom
try:
    from .private import custom as privateCustom
except ImportError:
    from .private.default import custom as privateCustom  # type: ignore

fields: List[data.CustomCommandField] = []
properties: List[str] = []
postProcess: List[data.CustomCommandProcess] = []
if privateCustom.disablePublic:
    fields = privateCustom.fields
    properties = privateCustom.properties
    postProcess = privateCustom.postProcess
else:
    fields = (publicCustom.fields + privateCustom.fields
              + publicCustom.fieldsEnd)
    properties = publicCustom.properties + privateCustom.properties
    postProcess = publicCustom.postProcess + privateCustom.postProcess
