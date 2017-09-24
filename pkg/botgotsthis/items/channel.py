from typing import Iterable, Mapping, Optional

from lib import data
from ..channel import block_url
from ..channel import broadcaster
from ..channel import custom
from ..channel import feature
from ..channel import mod
from ..channel import owner
from ..channel import reload
from ..channel import textformat


def filterMessage() -> Iterable[data.ChatCommand]:
    yield block_url.filterNoUrlForBots


def commands() -> Mapping[str, Optional[data.ChatCommand]]:
    if not hasattr(commands, 'commands'):
        setattr(commands, 'commands', {
            '!exit': owner.commandExit,
            '!managebot': owner.commandManageBot,
            '!reload': reload.commandReload,
            '!reloadcommands': reload.commandReloadCommands,
            '!reloadconfig': reload.commandReloadConfig,
            '!join': owner.commandJoin,
            '!part': owner.commandPart,
            '!emptychat': owner.commandEmpty,
            '!emptyall': owner.commandEmptyAll,
            '!global': custom.commandGlobal,
            '!say': owner.commandSay,
            '!hello': broadcaster.commandHello,
            '!leave': broadcaster.commandLeave,
            '!feature': feature.commandFeature,
            '!empty': broadcaster.commandEmpty,
            '!status': mod.commandStatus,
            '!title': mod.commandStatus,
            '!game': mod.commandGame,
            '!setgame': mod.commandRawGame,
            '!community': mod.commandCommunity,
            '!purge': mod.commandPurge,
            '!permit': mod.commandPermit,
            '!command': custom.commandCommand,
            '!full': textformat.commandFull,
            '!parenthesized': textformat.commandParenthesized,
            '!circled': textformat.commandCircled,
            '!smallcaps': textformat.commandSmallCaps,
            '!upsidedown': textformat.commandUpsideDown,
            '!serifbold': textformat.commandSerifBold,
            '!serif-bold': textformat.commandSerifBold,
            '!serifitalic': textformat.commandSerifItalic,
            '!serif-italic': textformat.commandSerifItalic,
            '!serifbolditalic': textformat.commandSerifBoldItalic,
            '!serif-bolditalic': textformat.commandSerifBoldItalic,
            '!serifbold-italic': textformat.commandSerifBoldItalic,
            '!serif-bold-italic': textformat.commandSerifBoldItalic,
            '!serifitalicbold': textformat.commandSerifBoldItalic,
            '!serif-italicbold': textformat.commandSerifBoldItalic,
            '!serifitalic-bold': textformat.commandSerifBoldItalic,
            '!serif-italic-bold': textformat.commandSerifBoldItalic,
            '!sanserif': textformat.commandSanSerif,
            '!sanserifbold': textformat.commandSanSerifBold,
            '!sanserif-bold': textformat.commandSanSerifBold,
            '!bold': textformat.commandSanSerifBold,
            '!sanserifitalic': textformat.commandSanSerifItalic,
            '!sanserif-italic': textformat.commandSanSerifItalic,
            '!italic': textformat.commandSanSerifItalic,
            '!sanserifbolditalic': textformat.commandSanSerifBoldItalic,
            '!sanserif-bolditalic': textformat.commandSanSerifBoldItalic,
            '!sanserifbold-italic': textformat.commandSanSerifBoldItalic,
            '!sanserif-bold-italic': textformat.commandSanSerifBoldItalic,
            '!bolditalic': textformat.commandSanSerifBoldItalic,
            '!bold-italic': textformat.commandSanSerifBoldItalic,
            '!sanserifitalicbold': textformat.commandSanSerifBoldItalic,
            '!sanserif-italicbold': textformat.commandSanSerifBoldItalic,
            '!sanserifitalic-bold': textformat.commandSanSerifBoldItalic,
            '!sanserif-italic-bold': textformat.commandSanSerifBoldItalic,
            '!italicbold': textformat.commandSanSerifBoldItalic,
            '!italic-bold': textformat.commandSanSerifBoldItalic,
            '!script': textformat.commandScript,
            '!cursive': textformat.commandScript,
            '!scriptbold': textformat.commandScriptBold,
            '!cursivebold': textformat.commandScriptBold,
            '!script-bold': textformat.commandScriptBold,
            '!cursive-bold': textformat.commandScriptBold,
            '!fraktur': textformat.commandFraktur,
            '!frakturbold': textformat.commandFrakturBold,
            '!fraktur-bold': textformat.commandFrakturBold,
            '!monospace': textformat.commandMonospace,
            '!doublestruck': textformat.commandDoubleStruck,
            '!come': broadcaster.commandCome,
            '!autojoin': broadcaster.commandAutoJoin,
            '!uptime': broadcaster.commandUptime,
            })
    return getattr(commands, 'commands')


def commandsStartWith() -> Mapping[str, Optional[data.ChatCommand]]:
    if not hasattr(commandsStartWith, 'commands'):
        setattr(commandsStartWith, 'commands', {
            '!settimeoutlevel-': broadcaster.commandSetTimeoutLevel,
            })
    return getattr(commandsStartWith, 'commands')


def processNoCommand() -> Iterable[data.ChatCommand]:
    yield custom.customCommands
