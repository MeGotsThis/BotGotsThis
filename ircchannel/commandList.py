from .nidoranRed import nidoranRed
from . import broadcaster
from . import reload
from . import full
from . import owner
from . import pyramid
from . import wall
from . import mod
from . import test

commands = {
    '!exit': (owner.commandExit, 'owner+ownerChan'),
    '!reload': (reload.commandReload, 'owner+ownerChan'),
    '!reloadcommands': (reload.commandReloadCommands, 'owner+ownerChan'),
    '!reloadconfig': (reload.commandReloadConfig, 'owner+ownerChan'),
    '!reloadallmods': (reload.commandReloadAllMods, 'owner+ownerChan'),
    '!listchats': (owner.commandListChats, 'owner+ownerChan'),
    '!join': (owner.commandJoin, 'admin+ownerChan'),
    '!part': (owner.commandPart, 'admin+ownerChan'),
    '!emptychat': (owner.commandEmpty, 'admin+ownerChan'),
    '!emptyall': (owner.commandEmptyAll, 'admin+ownerChan'),
    '!full': (full.commandFull, 'owner'),
    '!say': (owner.commandSay, 'owner'),
    '!e': (test.commandE, 'owner'),
    '!x': (test.commandX, 'owner'),
    '!y': (test.commandY, 'owner'),
    '!hello': (broadcaster.commandHello, 'broadcaster'),
    '!leave': (broadcaster.commandLeave, 'broadcaster'),
    '!empty': (broadcaster.commandEmpty, 'broadcaster'),
    '!pyramid': (pyramid.commandPyramid, 'broadcaster'),
    '!rpyramid': (pyramid.commandRPyramid, 'broadcaster'),
    '!wall': (wall.commandWall, 'broadcaster'),
    '!nidoran': (nidoranRed.commandNidoranRed, 'moderator'),
    '!reloadmods': (mod.commandReloadMods, 'moderator'),
    '!status': (mod.commandStatus, 'moderator'),
    '!title': (mod.commandStatus, 'moderator'),
    '!game': (mod.commandGame, 'moderator'),
    '!setgame': (mod.commandGame, 'moderator'),
    '!purge': (mod.commandPurge, 'moderator'),
    '!rekt': (mod.commandPurge, 'moderator'),
    '!dvs': (nidoranRed.commandDvs, None),
}
commandsStartWith = {
    '!pyramid-': (pyramid.commandPyramidLong, 'broadcaster'),
    '!wall-': (wall.commandWallLong, 'broadcaster'),
}
