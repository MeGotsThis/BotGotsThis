from source.public.whisper import broadcaster, feature, owner, reload

commands = {
    '!hello': owner.commandHello,
    '!exit': owner.commandExit,
    '!say': owner.commandSay,
    '!join': owner.commandJoin,
    '!part': owner.commandPart,
    '!emptychat': owner.commandEmpty,
    '!emptyall': owner.commandEmptyAll,
    '!managebot': owner.commandManageBot,
    '!reload': reload.commandReload,
    '!reloadcommands': reload.commandReloadCommands,
    '!reloadconfig': reload.commandReloadConfig,
    '!leave': broadcaster.commandLeave,
    '!empty': broadcaster.commandEmpty,
    '!come': broadcaster.commandCome,
    '!autojoin': broadcaster.commandAutoJoin,
    '!feature': feature.commandFeature,
    }
