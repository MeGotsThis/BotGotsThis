from source import data
from source.public.manage import autojoin, banned, listchats
from typing import Callable, Mapping, Optional

methods = {
    'listchats': listchats.manageListChats,
    'autojoin': autojoin.manageAutoJoin,
    'banned': banned.manageBanned,
    }  # type: Mapping[str, Optional[data.ManageBotCommand]]
