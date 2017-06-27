from source import data
from typing import Collection, Iterable, List  # noqa: F401
from .public import custom as publicCustom
try:
    from .private import custom as privateCustom
except ImportError:
    from .private.default import custom as privateCustom  # type: ignore


def fields() -> Iterable[data.CustomCommandField]:
    yield from privateCustom.fields()
    if not privateCustom.disablePublic():
        yield from publicCustom.fields()


def properties() -> Collection[str]:
    props: List[str] = list(privateCustom.properties())
    if not privateCustom.disablePublic():
        props.extend(publicCustom.properties())
    return props


def postProcess() -> Iterable[data.CustomCommandProcess]:
    if not privateCustom.disablePublic():
        yield from publicCustom.postProcess()
    yield from privateCustom.postProcess()
