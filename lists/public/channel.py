from source.public.channel import blockUrl
from source.public.channel import broadcaster
from source.public.channel import charConvert
from source.public.channel import feature
from source.public.channel import mod
from source.public.channel import owner
from source.public.channel import pyramid
from source.public.channel import reload
from source.public.channel import repeat
from source.public.channel import text
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
    '!serifbold': (charConvert.commandSerifBold, 'moderator'),
    '!serif-bold': (charConvert.commandSerifBold, 'moderator'),
    '!serifitalic': (charConvert.commandSerifItalic, 'moderator'),
    '!serif-italic': (charConvert.commandSerifItalic, 'moderator'),
    '!serifbolditalic': (charConvert.commandSerifBoldItalic, 'moderator'),
    '!serif-bolditalic': (charConvert.commandSerifBoldItalic, 'moderator'),
    '!serifbold-italic': (charConvert.commandSerifBoldItalic, 'moderator'),
    '!serif-bold-italic': (charConvert.commandSerifBoldItalic, 'moderator'),
    '!serifitalicbold': (charConvert.commandSerifBoldItalic, 'moderator'),
    '!serif-italicbold': (charConvert.commandSerifBoldItalic, 'moderator'),
    '!serifitalic-bold': (charConvert.commandSerifBoldItalic, 'moderator'),
    '!serif-italic-bold': (charConvert.commandSerifBoldItalic, 'moderator'),
    '!sanserif': (charConvert.commandSanSerif, 'moderator'),
    '!sanserifbold': (charConvert.commandSanSerifBold, 'moderator'),
    '!sanserif-bold': (charConvert.commandSanSerifBold, 'moderator'),
    '!bold': (charConvert.commandSanSerifBold, 'moderator'),
    '!sanserifitalic': (charConvert.commandSanSerifItalic, 'moderator'),
    '!sanserif-italic': (charConvert.commandSanSerifItalic, 'moderator'),
    '!italic': (charConvert.commandSanSerifItalic, 'moderator'),
    '!sanserifbolditalic': (charConvert.commandSanSerifBoldItalic,
                            'moderator'),
    '!sanserif-bolditalic': (charConvert.commandSanSerifBoldItalic,
                             'moderator'),
    '!sanserifbold-italic': (charConvert.commandSanSerifBoldItalic,
                             'moderator'),
    '!sanserif-bold-italic': (charConvert.commandSanSerifBoldItalic,
                              'moderator'),
    '!bolditalic': (charConvert.commandSanSerifBoldItalic, 'moderator'),
    '!bold-italic': (charConvert.commandSanSerifBoldItalic, 'moderator'),
    '!sanserifitalicbold': (charConvert.commandSanSerifBoldItalic,
                            'moderator'),
    '!sanserif-italicbold': (charConvert.commandSanSerifBoldItalic,
                             'moderator'),
    '!sanserifitalic-bold': (charConvert.commandSanSerifBoldItalic,
                             'moderator'),
    '!sanserif-italic-bold': (charConvert.commandSanSerifBoldItalic,
                              'moderator'),
    '!italicbold': (charConvert.commandSanSerifBoldItalic, 'moderator'),
    '!italic-bold': (charConvert.commandSanSerifBoldItalic, 'moderator'),
    '!script': (charConvert.commandScript, 'moderator'),
    '!cursive': (charConvert.commandScript, 'moderator'),
    '!scriptbold': (charConvert.commandScriptBold, 'moderator'),
    '!cursivebold': (charConvert.commandScriptBold, 'moderator'),
    '!script-bold': (charConvert.commandScriptBold, 'moderator'),
    '!cursive-bold': (charConvert.commandScriptBold, 'moderator'),
    '!fraktur': (charConvert.commandFraktur, 'moderator'),
    '!frakturbold': (charConvert.commandFrakturBold, 'moderator'),
    '!fraktur-bold': (charConvert.commandFrakturBold, 'moderator'),
    '!monospace': (charConvert.commandMonospace, 'moderator'),
    '!doublestruck': (charConvert.commandDoubleStruck, 'moderator'),
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

processNoCommand = [text.customCommands]
