from source.data.argument import ChatCommand
from typing import List, Mapping, Optional

disableFilters = False  # type: bool
disableCustomMessage = False  # type: bool

filterMessage = []  # type: List[ChatCommand]
commands = {}  # type: Mapping[str, Optional[ChatCommand]]
commandsStartWith = {}  # type: Mapping[str, Optional[ChatCommand]]
noCommandPreCustom = []  # type: List[ChatCommand]
noCommandPostCustom = []  # type: List[ChatCommand]
