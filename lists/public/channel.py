from source.public.channel import blockUrl, broadcaster, charConvert, feature
from source.public.channel import mod, owner, pyramid, reload, repeat, text
from source.public.channel import wall

filterMessage = [
    blockUrl.filterNoUrlForBots
    ]

commands = {
    '!exit': (owner.commandExit, 'owner+ownerChan'),
    '!managebot': (owner.commandManageBot, 'owner+ownerChan'),
    '!reload': (reload.commandReload, 'owner+ownerChan'),
    '!reloadcommands': (reload.commandReloadCommands, 'owner+ownerChan'),
    '!reloadconfig': (reload.commandReloadConfig, 'owner+ownerChan'),
    '!join': (owner.commandJoin, 'admin+ownerChan'),
    '!part': (owner.commandPart, 'admin+ownerChan'),
    '!emptychat': (owner.commandEmpty, 'admin+ownerChan'),
    '!emptyall': (owner.commandEmptyAll, 'admin+ownerChan'),
    '!global': (text.commandCommand, 'admin+ownerChan'),
    '!say': (owner.commandSay, 'owner+ownerChan'),
    '!hello': (broadcaster.commandHello, 'broadcaster'),
    '!leave': (broadcaster.commandLeave, 'broadcaster'),
    '!feature': (feature.commandFeature, 'broadcaster'),
    '!empty': (broadcaster.commandEmpty, 'broadcaster'),
    '!autorepeat': (repeat.commandAutoRepeat, 'broadcaster'),
    '!pyramid': (pyramid.commandPyramid, 'moderator'),
    '!rpyramid': (pyramid.commandRPyramid, 'moderator'),
    '!wall': (wall.commandWall, 'moderator'),
    '!status': (mod.commandStatus, 'moderator'),
    '!title': (mod.commandStatus, 'moderator'),
    '!game': (mod.commandGame, 'moderator'),
    '!setgame': (mod.commandGame, 'moderator'),
    '!purge': (mod.commandPurge, 'moderator'),
    '!rekt': (mod.commandPurge, 'moderator'),
    '!command': (text.commandCommand, 'moderator'),
    '!full': (charConvert.commandFull, 'moderator'),
    '!parenthesized': (charConvert.commandParenthesized, 'moderator'),
    '!circled': (charConvert.commandCircled, 'moderator'),
    '!smallcaps': (charConvert.commandSmallCaps, 'moderator'),
    '!upsidedown': (charConvert.commandUpsideDown, 'moderator'),
    '!come': (broadcaster.commandCome, 'ownerChan'),
    '!autojoin': (broadcaster.commandAutoJoin, 'ownerChan'),
    '!uptime': (broadcaster.commandUptime, None),
}
commandsStartWith = {
    '!pyramid-': (pyramid.commandPyramidLong, 'moderator'),
    '!wall-': (wall.commandWallLong, 'moderator'),
    '!autorepeat-': (repeat.commandAutoRepeat, 'broadcaster'),
}

processNoCommand = [text.customCommands]
