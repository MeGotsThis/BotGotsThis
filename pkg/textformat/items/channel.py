from typing import Iterable, Mapping, Optional

from lib import data
from .. import channel


def filterMessage() -> Iterable[data.ChatCommand]:
    return []


def commands() -> Mapping[str, Optional[data.ChatCommand]]:
    if not hasattr(commands, 'commands'):
        setattr(commands, 'commands', {
            '!full': channel.commandFull,
            '!parenthesized': channel.commandParenthesized,
            '!circled': channel.commandCircled,
            '!smallcaps': channel.commandSmallCaps,
            '!upsidedown': channel.commandUpsideDown,
            '!serifbold': channel.commandSerifBold,
            '!serif-bold': channel.commandSerifBold,
            '!serifitalic': channel.commandSerifItalic,
            '!serif-italic': channel.commandSerifItalic,
            '!serifbolditalic': channel.commandSerifBoldItalic,
            '!serif-bolditalic': channel.commandSerifBoldItalic,
            '!serifbold-italic': channel.commandSerifBoldItalic,
            '!serif-bold-italic': channel.commandSerifBoldItalic,
            '!serifitalicbold': channel.commandSerifBoldItalic,
            '!serif-italicbold': channel.commandSerifBoldItalic,
            '!serifitalic-bold': channel.commandSerifBoldItalic,
            '!serif-italic-bold': channel.commandSerifBoldItalic,
            '!sanserif': channel.commandSanSerif,
            '!sanserifbold': channel.commandSanSerifBold,
            '!sanserif-bold': channel.commandSanSerifBold,
            '!bold': channel.commandSanSerifBold,
            '!sanserifitalic': channel.commandSanSerifItalic,
            '!sanserif-italic': channel.commandSanSerifItalic,
            '!italic': channel.commandSanSerifItalic,
            '!sanserifbolditalic': channel.commandSanSerifBoldItalic,
            '!sanserif-bolditalic': channel.commandSanSerifBoldItalic,
            '!sanserifbold-italic': channel.commandSanSerifBoldItalic,
            '!sanserif-bold-italic': channel.commandSanSerifBoldItalic,
            '!bolditalic': channel.commandSanSerifBoldItalic,
            '!bold-italic': channel.commandSanSerifBoldItalic,
            '!sanserifitalicbold': channel.commandSanSerifBoldItalic,
            '!sanserif-italicbold': channel.commandSanSerifBoldItalic,
            '!sanserifitalic-bold': channel.commandSanSerifBoldItalic,
            '!sanserif-italic-bold': channel.commandSanSerifBoldItalic,
            '!italicbold': channel.commandSanSerifBoldItalic,
            '!italic-bold': channel.commandSanSerifBoldItalic,
            '!script': channel.commandScript,
            '!cursive': channel.commandScript,
            '!scriptbold': channel.commandScriptBold,
            '!cursivebold': channel.commandScriptBold,
            '!script-bold': channel.commandScriptBold,
            '!cursive-bold': channel.commandScriptBold,
            '!fraktur': channel.commandFraktur,
            '!frakturbold': channel.commandFrakturBold,
            '!fraktur-bold': channel.commandFrakturBold,
            '!monospace': channel.commandMonospace,
            '!doublestruck': channel.commandDoubleStruck,
            })
    return getattr(commands, 'commands')


def commandsStartWith() -> Mapping[str, Optional[data.ChatCommand]]:
    return {}


def processNoCommand() -> Iterable[data.ChatCommand]:
    return []
