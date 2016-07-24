from typing import Callable
from ..library import textformat
from ..library.chat import feature, min_args, permission
from ...data import ChatCommand, ChatCommandArgs


def text_command(name: str, asciiTo: Callable[[str], str]) -> ChatCommand:
    @feature('textconvert')
    @min_args(2)
    @permission('moderator')
    def command(args: ChatCommandArgs) -> bool:
        args.chat.send(asciiTo(args.message.query))
        return True
    command.__name__ = name
    return command

commandFull = text_command('commandFull', textformat.to_full_width)  # type: ChatCommand
commandParenthesized = text_command(
    'commandParenthesized', textformat.to_parenthesized)  # type: ChatCommand
commandCircled = text_command('commandCircled', textformat.to_circled)  # type: ChatCommand
commandSmallCaps = text_command('commandSmallCaps', textformat.to_small_caps)  # type: ChatCommand
commandUpsideDown = text_command(
    'commandUpsideDown', textformat.to_upside_down)  # type: ChatCommand
commandSerifBold = text_command('commandSerifBold', textformat.to_serif_bold)  # type: ChatCommand
commandSerifItalic = text_command(
    'commandSerifItalic', textformat.to_serif_italic)  # type: ChatCommand
commandSerifBoldItalic = text_command(
    'commandSerifBoldItalic', textformat.to_serif_bold_italic)  # type: ChatCommand
commandSanSerif = text_command('commandSanSerif', textformat.to_sanserif)  # type: ChatCommand
commandSanSerifBold = text_command(
    'commandSanSerifBold', textformat.to_sanserif_bold)  # type: ChatCommand
commandSanSerifItalic = text_command(
    'commandSanSerifItalic', textformat.to_sanserif_italic)  # type: ChatCommand
commandSanSerifBoldItalic = text_command(
    'commandSanSerifBoldItalic', textformat.to_sanserif_bold_italic)  # type: ChatCommand
commandScript = text_command('commandScript', textformat.to_script)  # type: ChatCommand
commandScriptBold = text_command(
    'commandScriptBold', textformat.to_script_bold)  # type: ChatCommand
commandFraktur = text_command('commandFraktur', textformat.to_fraktur)  # type: ChatCommand
commandFrakturBold = text_command(
    'commandFrakturBold', textformat.to_fraktur_bold)  # type: ChatCommand
commandMonospace = text_command('commandMonospace', textformat.to_monospace)  # type: ChatCommand
commandDoubleStruck = text_command(
    'commandDoubleStruck', textformat.to_double_struck)  # type: ChatCommand
