from source.public.channel import blockUrl
from source.public.channel import broadcaster
from source.public.channel import custom
from source.public.channel import feature
from source.public.channel import mod
from source.public.channel import owner
from source.public.channel import pyramid
from source.public.channel import reload
from source.public.channel import repeat
from source.public.channel import textformat
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
    '!global': (custom.commandCommand, 'admin+ownerChan'),
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
    '!command': (custom.commandCommand, 'moderator'),
    '!full': (textformat.commandFull, 'moderator'),
    '!parenthesized': (textformat.commandParenthesized, 'moderator'),
    '!circled': (textformat.commandCircled, 'moderator'),
    '!smallcaps': (textformat.commandSmallCaps, 'moderator'),
    '!upsidedown': (textformat.commandUpsideDown, 'moderator'),
    '!serifbold': (textformat.commandSerifBold, 'moderator'),
    '!serif-bold': (textformat.commandSerifBold, 'moderator'),
    '!serifitalic': (textformat.commandSerifItalic, 'moderator'),
    '!serif-italic': (textformat.commandSerifItalic, 'moderator'),
    '!serifbolditalic': (textformat.commandSerifBoldItalic, 'moderator'),
    '!serif-bolditalic': (textformat.commandSerifBoldItalic, 'moderator'),
    '!serifbold-italic': (textformat.commandSerifBoldItalic, 'moderator'),
    '!serif-bold-italic': (textformat.commandSerifBoldItalic, 'moderator'),
    '!serifitalicbold': (textformat.commandSerifBoldItalic, 'moderator'),
    '!serif-italicbold': (textformat.commandSerifBoldItalic, 'moderator'),
    '!serifitalic-bold': (textformat.commandSerifBoldItalic, 'moderator'),
    '!serif-italic-bold': (textformat.commandSerifBoldItalic, 'moderator'),
    '!sanserif': (textformat.commandSanSerif, 'moderator'),
    '!sanserifbold': (textformat.commandSanSerifBold, 'moderator'),
    '!sanserif-bold': (textformat.commandSanSerifBold, 'moderator'),
    '!bold': (textformat.commandSanSerifBold, 'moderator'),
    '!sanserifitalic': (textformat.commandSanSerifItalic, 'moderator'),
    '!sanserif-italic': (textformat.commandSanSerifItalic, 'moderator'),
    '!italic': (textformat.commandSanSerifItalic, 'moderator'),
    '!sanserifbolditalic': (textformat.commandSanSerifBoldItalic,
                            'moderator'),
    '!sanserif-bolditalic': (textformat.commandSanSerifBoldItalic,
                             'moderator'),
    '!sanserifbold-italic': (textformat.commandSanSerifBoldItalic,
                             'moderator'),
    '!sanserif-bold-italic': (textformat.commandSanSerifBoldItalic,
                              'moderator'),
    '!bolditalic': (textformat.commandSanSerifBoldItalic, 'moderator'),
    '!bold-italic': (textformat.commandSanSerifBoldItalic, 'moderator'),
    '!sanserifitalicbold': (textformat.commandSanSerifBoldItalic,
                            'moderator'),
    '!sanserif-italicbold': (textformat.commandSanSerifBoldItalic,
                             'moderator'),
    '!sanserifitalic-bold': (textformat.commandSanSerifBoldItalic,
                             'moderator'),
    '!sanserif-italic-bold': (textformat.commandSanSerifBoldItalic,
                              'moderator'),
    '!italicbold': (textformat.commandSanSerifBoldItalic, 'moderator'),
    '!italic-bold': (textformat.commandSanSerifBoldItalic, 'moderator'),
    '!script': (textformat.commandScript, 'moderator'),
    '!cursive': (textformat.commandScript, 'moderator'),
    '!scriptbold': (textformat.commandScriptBold, 'moderator'),
    '!cursivebold': (textformat.commandScriptBold, 'moderator'),
    '!script-bold': (textformat.commandScriptBold, 'moderator'),
    '!cursive-bold': (textformat.commandScriptBold, 'moderator'),
    '!fraktur': (textformat.commandFraktur, 'moderator'),
    '!frakturbold': (textformat.commandFrakturBold, 'moderator'),
    '!fraktur-bold': (textformat.commandFrakturBold, 'moderator'),
    '!monospace': (textformat.commandMonospace, 'moderator'),
    '!doublestruck': (textformat.commandDoubleStruck, 'moderator'),
    '!come': (broadcaster.commandCome, 'ownerChan'),
    '!autojoin': (broadcaster.commandAutoJoin, 'ownerChan'),
    '!uptime': (broadcaster.commandUptime, None),
}
commandsStartWith = {
    '!pyramid-': (pyramid.commandPyramidLong, 'moderator'),
    '!wall-': (wall.commandWallLong, 'moderator'),
    '!autorepeat-': (repeat.commandAutoRepeat, 'broadcaster'),
    '!settimeoutlevel-': (broadcaster.commandSetTimeoutLevel, 'broadcaster'),
}

processNoCommand = [custom.customCommands]
