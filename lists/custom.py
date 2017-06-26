from source import data
from typing import List
from .public import custom as publicCustom
try:
    from .private import custom as privateCustom
except ImportError:
    from .private.default import custom as privateCustom  # type: ignore


def fields() -> List[data.CustomCommandField]:
    if privateCustom.disablePublic():
        return privateCustom.fields()
    else:
        return (publicCustom.fields()
                + privateCustom.fields()
                + publicCustom.fieldsEnd())


def properties() -> List[str]:
    if privateCustom.disablePublic():
        return privateCustom.properties()
    else:
        return publicCustom.properties() + privateCustom.properties()


def postProcess() -> List[data.CustomCommandProcess]:
    if privateCustom.disablePublic():
        return privateCustom.postProcess()
    else:
        return publicCustom.postProcess() + privateCustom.postProcess()
