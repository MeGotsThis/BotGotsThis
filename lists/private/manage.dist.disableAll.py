from source.data import ManageBotCommand
from typing import Mapping, Optional


def methods() -> Mapping[str, Optional[ManageBotCommand]]:
    return {
        'listchats': None,
        'autojoin': None,
        'banned': None,
        }
