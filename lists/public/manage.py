from source import data
from source.public.manage import autojoin, banned, listchats, manager
from typing import Mapping, Optional

methods = {
    'listchats': listchats.manageListChats,
    'autojoin': autojoin.manageAutoJoin,
    'banned': banned.manageBanned,
    'manager': manager.manageManager,
    }  # type: Mapping[str, Optional[data.ManageBotCommand]]
