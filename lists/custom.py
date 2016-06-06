from source.data.argument import CustomFieldArgs, CustomProcessArgs
from typing import Callable, List, Optional
from .public import custom as publicCustom
try:
    from .private import custom as privateCustom
except ImportError:
    from .private.default import custom as privateCustom  # type: ignore

fields = []  # type: List[Callable[[CustomFieldArgs], Optional[str]]]
properties = []  # type: List[str]
postProcess = []  # type: List[Callable[[CustomProcessArgs], Optional[str]]]
if privateCustom.disablePublic:
    fields = privateCustom.fields
    properties = privateCustom.properties
    postProcess = privateCustom.postProcess
else:
    fields = (publicCustom.fields + privateCustom.fields
              + publicCustom.fieldsEnd)
    properties = publicCustom.properties + privateCustom.properties
    postProcess = publicCustom.postProcess + privateCustom.postProcess
