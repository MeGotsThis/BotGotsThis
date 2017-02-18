from source.data import ChatCommand
from typing import List, Mapping, Optional

disableFilters: bool = False
disableCustomMessage: bool = False

filterMessage: List[ChatCommand] = []
commands: Mapping[str, Optional[ChatCommand]] = {}
commandsStartWith: Mapping[str, Optional[ChatCommand]] = {}
noCommandPreCustom: List[ChatCommand] = []
noCommandPostCustom: List[ChatCommand] = []
