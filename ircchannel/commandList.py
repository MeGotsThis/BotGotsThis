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
    '!reloadCommands': (reload.commandReloadCommands, 'owner+ownerChan'),
    '!join': (owner.commandJoin, 'owner+ownerChan'),
    '!part': (owner.commandPart, 'owner+ownerChan'),
    '!emptyall': (owner.commandEmptyAll, 'owner+ownerChan'),
    '!emptychan': (owner.commandEmpty, 'owner+ownerChan'),
    '!listchats': (owner.commandListChats, 'owner+ownerChan'),
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
