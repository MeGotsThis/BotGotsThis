from typing import Callable
from ..library import textformat
from ..library.chat import feature, min_args, permission
from ...data import ChatCommandArgs


def textCommand(name: str, asciiTo: Callable[[str], str]):
    @feature('textconvert')
    @min_args(2)
    @permission('moderator')
    def command(args: ChatCommandArgs) -> bool:
        args.chat.send(asciiTo(args.message.query))
        return True
    command.__name__ = name
    return command

commandFull = textCommand('commandFull', textformat.to_full_width)
commandParenthesized = textCommand(
    'commandParenthesized', textformat.to_parenthesized)
commandCircled = textCommand('commandCircled', textformat.to_circled)
commandSmallCaps = textCommand('commandSmallCaps', textformat.to_small_caps)
commandUpsideDown = textCommand('commandUpsideDown', textformat.to_upside_down)
commandSerifBold = textCommand('commandSerifBold', textformat.to_serif_bold)
commandSerifItalic = textCommand(
    'commandSerifItalic', textformat.to_serif_italic)
commandSerifBoldItalic = textCommand(
    'commandSerifBoldItalic', textformat.to_serif_bold_italic)
commandSanSerif = textCommand('commandSanSerif', textformat.to_sanserif)
commandSanSerifBold = textCommand(
    'commandSanSerifBold', textformat.to_sanserif_bold)
commandSanSerifItalic = textCommand(
    'commandSanSerifItalic', textformat.to_sanserif_italic)
commandSanSerifBoldItalic = textCommand(
    'commandSanSerifBoldItalic', textformat.to_sanserif_bold_italic)
commandScript = textCommand('commandScript', textformat.to_script)
commandScriptBold = textCommand('commandScriptBold', textformat.to_script_bold)
commandFraktur = textCommand('commandFraktur', textformat.to_fraktur)
commandFrakturBold = textCommand('commandFrakturBold', textformat.to_fraktur_bold)
commandMonospace = textCommand('commandMonospace', textformat.to_monospace)
commandDoubleStruck = textCommand(
    'commandDoubleStruck', textformat.to_double_struck)
