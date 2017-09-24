from typing import Iterable, Mapping, Optional

from lib import data
from ..channel import textformat


def filterMessage() -> Iterable[data.ChatCommand]:
    return []


def commands() -> Mapping[str, Optional[data.ChatCommand]]:
    if not hasattr(commands, 'commands'):
        setattr(commands, 'commands', {
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
            })
    return getattr(commands, 'commands')


def commandsStartWith() -> Mapping[str, Optional[data.ChatCommand]]:
    return {}


def processNoCommand() -> Iterable[data.ChatCommand]:
    return []
