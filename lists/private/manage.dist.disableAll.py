from source.data import ManageBotCommand
from typing import Mapping, Optional


def methods() -> Mapping[str, Optional[ManageBotCommand]]:
    if not hasattr(methods, 'methods'):
        setattr(methods, 'methods', {
            'listchats': None,
            'autojoin': None,
            'banned': None,
            })
    return getattr(methods, 'methods')
