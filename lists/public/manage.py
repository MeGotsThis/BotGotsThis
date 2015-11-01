from source.public.manage import autojoin, banned, listchats

methods = {
    'listchats': listchats.manageListChats,
    'autojoin': autojoin.manageAutoJoin,
    'banned': banned.manageBanned,
    }
