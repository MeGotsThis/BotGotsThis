from source.data import CustomCommandField, CustomCommandProcess
from typing import List


def disablePublic() -> bool:
    return False


def fields() -> List[CustomCommandField]:
    return []


def properties() -> List[str]:
    return []


def postProcess() -> List[CustomCommandProcess]:
    return []
