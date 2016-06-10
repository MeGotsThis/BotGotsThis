from typing import Callable
from ..library import textformat
from ..library.chat import feature, min_args, permission
from ...data.argument import ChatCommandArgs


def textCommand(name: str, asciiTo: Callable[[str], str]):
    @feature('textconvert')
    @min_args(2)
    @permission('moderator')
    def command(args: ChatCommandArgs) -> bool:
        args.chat.send(asciiTo(args.message.query))
        return True
    command.__name__ = name
    return command

commandFull = textCommand('commandFull', textformat.asciiToFullWidth)
commandParenthesized = textCommand(
    'commandParenthesized', textformat.asciiToParenthesized)
commandCircled = textCommand('commandCircled', textformat.asciiToCircled)
commandSmallCaps = textCommand('commandSmallCaps', textformat.asciiToSmallCaps)
commandUpsideDown = textCommand(
    'commandUpsideDown', textformat.asciiToUpsideDown)
commandSerifBold = textCommand('commandSerifBold', textformat.asciiToSerifBold)
commandSerifItalic = textCommand(
    'commandSerifItalic', textformat.asciiToSerifItalic)
commandSerifBoldItalic = textCommand(
    'commandSerifBoldItalic', textformat.asciiToSerifBoldItalic)
commandSanSerif = textCommand('commandSanSerif', textformat.asciiToSanSerif)
commandSanSerifBold = textCommand(
    'commandSanSerifBold', textformat.asciiToSanSerifBold)
commandSanSerifItalic = textCommand(
    'commandSanSerifItalic', textformat.asciiToSanSerifItalic)
commandSanSerifBoldItalic = textCommand(
    'commandSanSerifBoldItalic', textformat.asciiToSanSerifBoldItalic)
commandScript = textCommand('commandScript', textformat.asciiToScript)
commandScriptBold = textCommand(
    'commandScriptBold', textformat.asciiToScriptBold)
commandFraktur = textCommand('commandFraktur', textformat.asciiToFraktur)
commandFrakturBold = textCommand(
    'commandFrakturBold', textformat.asciiToFrakturBold)
commandMonospace = textCommand('commandMonospace', textformat.asciiToMonospace)
commandDoubleStruck = textCommand(
    'commandDoubleStruck', textformat.asciiToDoubleStruck)
