from source import data
from source.public.manage import autojoin, banned, listchats, manager
from typing import Mapping, Optional

methods: Mapping[str, Optional[data.ManageBotCommand]] = {
    'listchats': listchats.manageListChats,
    'autojoin': autojoin.manageAutoJoin,
    'banned': banned.manageBanned,
    'manager': manager.manageManager,
    }
