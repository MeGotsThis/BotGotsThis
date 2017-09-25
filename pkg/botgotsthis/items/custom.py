from lib import data
from typing import Collection, Iterable


def fields() -> Iterable[data.CustomCommandField]:
    return []


def properties() -> Collection[str]:
    return []


def postProcess() -> Iterable[data.CustomCommandProcess]:
    return []
