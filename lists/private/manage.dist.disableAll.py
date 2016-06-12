from source.data.argument import ManageBotCommand
from typing import Callable, Mapping, Optional

methods = {
    'listchats': None,
    'autojoin': None,
    'banned': None,
    }  # type: Mapping[str, Optional[ManageBotCommand]]
