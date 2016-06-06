from source.data.argument import CustomFieldArgs, CustomProcessArgs
from typing import Callable, List, Optional

disablePublic = False  # type: bool

fields = [] # type: List[Callable[[CustomFieldArgs], Optional[str]]]
properties = [] # type: List[str]
postProcess = [] # type: List[Callable[[CustomProcessArgs], Optional[str]]]
