from source.data.argument import ManageBotArgs
from typing import Callable, Mapping, Optional

methods = {
    'listchats': None,
    'autojoin': None,
    'banned': None,
    }  # type: Mapping[str, Optional[Callable[[ManageBotArgs], bool]]]
