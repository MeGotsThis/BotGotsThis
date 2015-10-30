from source.public.whisper import broadcaster, feature, owner, reload

commands = {
    '!hello': (owner.commandHello, 'owner'),
    '!exit': (owner.commandExit, 'owner'),
    '!say': (owner.commandSay, 'owner'),
    '!join': (owner.commandJoin, 'admin'),
    '!part': (owner.commandPart, 'admin'),
    '!emptychat': (owner.commandEmpty, 'admin'),
    '!emptyall': (owner.commandEmptyAll, 'admin'),
    '!managebot': (owner.commandManageBot, 'owner'),
    '!reload': (reload.commandReload, 'owner'),
    '!reloadcommands': (reload.commandReloadCommands, 'owner'),
    '!reloadconfig': (reload.commandReloadConfig, 'owner'),
    '!leave': (broadcaster.commandLeave, None),
    '!empty': (broadcaster.commandEmpty, None),
    '!come': (broadcaster.commandCome, None),
    '!autojoin': (broadcaster.commandAutoJoin, None),
    '!feature': (feature.commandFeature, None),
    }
