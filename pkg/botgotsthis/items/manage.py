from lib import data
from ..manage import autojoin, banned, listchats, manager
from typing import Mapping, Optional


def methods() -> Mapping[str, Optional[data.ManageBotCommand]]:
    if not hasattr(methods, 'methods'):
        setattr(methods, 'methods', {
            'listchats': listchats.manageListChats,
            'autojoin': autojoin.manageAutoJoin,
            'banned': banned.manageBanned,
            'manager': manager.manageManager,
            })
    return getattr(methods, 'methods')
