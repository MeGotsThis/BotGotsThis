import ircchannel.broadcaster
import ircchannel.reload
import ircchannel.full
import ircchannel.owner
import ircchannel.pyramid
import ircchannel.wall
import ircchannel.mod
import ircchannel.text
import privatechannel.commandList

commands = {
    '!exit': (ircchannel.owner.commandExit, 'owner+ownerChan'),
    '!managebot': (ircchannel.owner.commandManageBot, 'owner+ownerChan'),
    '!reload': (ircchannel.reload.commandReload, 'owner+ownerChan'),
    '!reloadcommands':
    (ircchannel.reload.commandReloadCommands, 'owner+ownerChan'),
    '!reloadconfig':
    (ircchannel.reload.commandReloadConfig, 'owner+ownerChan'),
    '!reloadallmods':
    (ircchannel.reload.commandReloadAllMods, 'owner+ownerChan'),
    '!join': (ircchannel.owner.commandJoin, 'admin+ownerChan'),
    '!part': (ircchannel.owner.commandPart, 'admin+ownerChan'),
    '!emptychat': (ircchannel.owner.commandEmpty, 'admin+ownerChan'),
    '!emptyall': (ircchannel.owner.commandEmptyAll, 'admin+ownerChan'),
    '!global': (ircchannel.text.commandCommand, 'admin+ownerChan'),
    '!say': (ircchannel.owner.commandSay, 'owner'),
    '!hello': (ircchannel.broadcaster.commandHello, 'broadcaster'),
    '!leave': (ircchannel.broadcaster.commandLeave, 'broadcaster'),
    '!empty': (ircchannel.broadcaster.commandEmpty, 'broadcaster'),
    '!pyramid': (ircchannel.pyramid.commandPyramid, 'broadcaster'),
    '!rpyramid': (ircchannel.pyramid.commandRPyramid, 'broadcaster'),
    '!wall': (ircchannel.wall.commandWall, 'broadcaster'),
    '!reloadmods': (ircchannel.mod.commandReloadMods, 'moderator'),
    '!status': (ircchannel.mod.commandStatus, 'moderator'),
    '!title': (ircchannel.mod.commandStatus, 'moderator'),
    '!game': (ircchannel.mod.commandGame, 'moderator'),
    '!setgame': (ircchannel.mod.commandGame, 'moderator'),
    '!purge': (ircchannel.mod.commandPurge, 'moderator'),
    '!rekt': (ircchannel.mod.commandPurge, 'moderator'),
    '!command': (ircchannel.text.commandCommand, 'moderator'),
    '!full': (ircchannel.full.commandFull, 'moderator'),
    '!come': (ircchannel.broadcaster.commandCome, 'ownerChan'),
    '!autojoin': (ircchannel.broadcaster.commandAutoJoin, 'ownerChan'),
}
commandsStartWith = {
    '!pyramid-': (ircchannel.pyramid.commandPyramidLong, 'broadcaster'),
    '!wall-': (ircchannel.wall.commandWallLong, 'broadcaster'),
}

commands = dict(
    list(commands.items()) + list(privatechannel.commandList.commands.items()))
commandsStartWith = dict(
    list(commandsStartWith.items()) +
    list(privatechannel.commandList.commandsStartWith.items()))
