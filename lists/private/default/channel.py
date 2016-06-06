from source.data.argument import ChatCommandArgs
from typing import Callable, List, Mapping, Optional

disableFilters = False  # type: bool
disableCustomMessage = False  # type: bool

filterMessage = []  # type: List[Callable[[ChatCommandArgs], bool]]
commands = {}  # type: Mapping[str, Optional[Callable[[ChatCommandArgs], bool]]]
commandsStartWith = {}  # type: Mapping[str, Optional[Callable[[ChatCommandArgs], bool]]]
noCommandPreCustom = []  # type: List[Callable[[ChatCommandArgs], bool]]
noCommandPostCustom = []  # type: List[Callable[[ChatCommandArgs], bool]]
