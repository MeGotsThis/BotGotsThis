from source.data import CustomCommandField, CustomCommandProcess
from typing import Collection, Iterable


def disablePublic() -> bool:
    return True


def fields() -> Iterable[CustomCommandField]:
    return []


def properties() -> Collection[str]:
    return []


def postProcess() -> Iterable[CustomCommandProcess]:
    return []
