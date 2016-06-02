from source.public.whisper import broadcaster, feature, owner, reload

commands = {
    '!hello': (owner.commandHello, None),
    '!exit': (owner.commandExit, None),
    '!say': (owner.commandSay, None),
    '!join': (owner.commandJoin, 'admin'),
    '!part': (owner.commandPart, 'admin'),
    '!emptychat': (owner.commandEmpty, 'admin'),
    '!emptyall': (owner.commandEmptyAll, 'admin'),
    '!managebot': (owner.commandManageBot, None),
    '!reload': (reload.commandReload, None),
    '!reloadcommands': (reload.commandReloadCommands, None),
    '!reloadconfig': (reload.commandReloadConfig, None),
    '!leave': (broadcaster.commandLeave, None),
    '!empty': (broadcaster.commandEmpty, None),
    '!come': (broadcaster.commandCome, None),
    '!autojoin': (broadcaster.commandAutoJoin, None),
    '!feature': (feature.commandFeature, None),
    }
