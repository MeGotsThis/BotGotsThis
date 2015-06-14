import ircchannel.broadcaster
import ircchannel.charConvert
import ircchannel.feature
import ircchannel.reload
import ircchannel.owner
import ircchannel.pyramid
import ircchannel.wall
import ircchannel.mod
import ircchannel.text
import ircchannel.repeat
try:
    import privatechannel.commandList as commandList
except:
    import privatechannel.default.commandList as commandList

commands = {
    '!exit': (ircchannel.owner.commandExit, 'owner+ownerChan'),
    '!managebot': (ircchannel.owner.commandManageBot, 'owner+ownerChan'),
    '!reload': (ircchannel.reload.commandReload, 'owner+ownerChan'),
    '!reloadcommands':
    (ircchannel.reload.commandReloadCommands, 'owner+ownerChan'),
    '!reloadconfig':
    (ircchannel.reload.commandReloadConfig, 'owner+ownerChan'),
    '!join': (ircchannel.owner.commandJoin, 'admin+ownerChan'),
    '!part': (ircchannel.owner.commandPart, 'admin+ownerChan'),
    '!emptychat': (ircchannel.owner.commandEmpty, 'admin+ownerChan'),
    '!emptyall': (ircchannel.owner.commandEmptyAll, 'admin+ownerChan'),
    '!global': (ircchannel.text.commandCommand, 'admin+ownerChan'),
    '!say': (ircchannel.owner.commandSay, 'owner+ownerChan'),
    '!hello': (ircchannel.broadcaster.commandHello, 'broadcaster'),
    '!leave': (ircchannel.broadcaster.commandLeave, 'broadcaster'),
    '!feature': (ircchannel.feature.commandFeature, 'broadcaster'),
    '!empty': (ircchannel.broadcaster.commandEmpty, 'broadcaster'),
    '!autorepeat': (ircchannel.repeat.commandAutoRepeat, 'broadcaster'),
    '!pyramid': (ircchannel.pyramid.commandPyramid, 'moderator'),
    '!rpyramid': (ircchannel.pyramid.commandRPyramid, 'moderator'),
    '!wall': (ircchannel.wall.commandWall, 'moderator'),
    '!status': (ircchannel.mod.commandStatus, 'moderator'),
    '!title': (ircchannel.mod.commandStatus, 'moderator'),
    '!game': (ircchannel.mod.commandGame, 'moderator'),
    '!setgame': (ircchannel.mod.commandGame, 'moderator'),
    '!purge': (ircchannel.mod.commandPurge, 'moderator'),
    '!rekt': (ircchannel.mod.commandPurge, 'moderator'),
    '!command': (ircchannel.text.commandCommand, 'moderator'),
    '!full': (ircchannel.charConvert.commandFull, 'moderator'),
    '!parenthesized':
    (ircchannel.charConvert.commandParenthesized, 'moderator'),
    '!circled': (ircchannel.charConvert.commandCircled, 'moderator'),
    '!smallcaps': (ircchannel.charConvert.commandSmallCaps, 'moderator'),
    '!upsidedown': (ircchannel.charConvert.commandUpsideDown, 'moderator'),
    '!come': (ircchannel.broadcaster.commandCome, 'ownerChan'),
    '!autojoin': (ircchannel.broadcaster.commandAutoJoin, 'ownerChan'),
    '!uptime': (ircchannel.broadcaster.commandUptime, None),
}
commandsStartWith = {
    '!pyramid-': (ircchannel.pyramid.commandPyramidLong, 'moderator'),
    '!wall-': (ircchannel.wall.commandWallLong, 'moderator'),
    '!autorepeat-': (ircchannel.repeat.commandAutoRepeat, 'broadcaster'),
}

commands = dict(list(commands.items()) + list(commandList.commands.items()))
commandsStartWith = dict(
    list(commandsStartWith.items()) +
    list(commandList.commandsStartWith.items()))
