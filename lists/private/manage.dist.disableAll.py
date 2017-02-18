from source.data import ManageBotCommand
from typing import Mapping, Optional

methods: Mapping[str, Optional[ManageBotCommand]] = {
    'listchats': None,
    'autojoin': None,
    'banned': None,
    }
