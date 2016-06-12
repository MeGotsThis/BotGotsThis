from source.data import CustomCommandField, CustomCommandProcess
from typing import Callable, List, Optional

disablePublic = False  # type: bool

fields = [] # type: List[CustomCommandField]
properties = [] # type: List[str]
postProcess = [] # type: List[CustomCommandProcess]
