from typing import Callable

from source.data import ChatCommand, ChatCommandArgs
from source.helper.chat import feature, min_args, permission
from source.helper import textformat


def text_command(name: str, asciiTo: Callable[[str], str]) -> ChatCommand:
    @feature('textconvert')
    @min_args(2)
    @permission('moderator')
    async def command(args: ChatCommandArgs) -> bool:
        args.chat.send(asciiTo(args.message.query))
        return True
    command.__name__ = name
    return command


commandFull: ChatCommand = text_command(
    'commandFull', textformat.to_full_width)
commandParenthesized: ChatCommand = text_command(
    'commandParenthesized', textformat.to_parenthesized)
commandCircled: ChatCommand = text_command(
    'commandCircled', textformat.to_circled)
commandSmallCaps: ChatCommand = text_command(
    'commandSmallCaps', textformat.to_small_caps)
commandUpsideDown: ChatCommand = text_command(
    'commandUpsideDown', textformat.to_upside_down)
commandSerifBold: ChatCommand = text_command(
    'commandSerifBold', textformat.to_serif_bold)
commandSerifItalic: ChatCommand = text_command(
    'commandSerifItalic', textformat.to_serif_italic)
commandSerifBoldItalic: ChatCommand = text_command(
    'commandSerifBoldItalic', textformat.to_serif_bold_italic)
commandSanSerif: ChatCommand = text_command(
    'commandSanSerif', textformat.to_sanserif)
commandSanSerifBold: ChatCommand = text_command(
    'commandSanSerifBold', textformat.to_sanserif_bold)
commandSanSerifItalic: ChatCommand = text_command(
    'commandSanSerifItalic', textformat.to_sanserif_italic)
commandSanSerifBoldItalic: ChatCommand = text_command(
    'commandSanSerifBoldItalic', textformat.to_sanserif_bold_italic)
commandScript: ChatCommand = text_command(
    'commandScript', textformat.to_script)
commandScriptBold: ChatCommand = text_command(
    'commandScriptBold', textformat.to_script_bold)
commandFraktur: ChatCommand = text_command(
    'commandFraktur', textformat.to_fraktur)
commandFrakturBold: ChatCommand = text_command(
    'commandFrakturBold', textformat.to_fraktur_bold)
commandMonospace: ChatCommand = text_command(
    'commandMonospace', textformat.to_monospace)
commandDoubleStruck: ChatCommand = text_command(
    'commandDoubleStruck', textformat.to_double_struck)
