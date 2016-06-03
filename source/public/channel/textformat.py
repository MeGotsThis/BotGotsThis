from ..library import textformat
from ..library.chat import feature, min_args, permission

@feature('textconvert')
@min_args(2)
@permission('moderator')
def commandFull(args):
    args.chat.send(textformat.asciiToFullWidth(args.message.query))
    return True

@feature('textconvert')
@min_args(2)
@permission('moderator')
def commandParenthesized(args):
    args.chat.send(textformat.asciiToParenthesized(args.message.query))
    return True

@feature('textconvert')
@min_args(2)
@permission('moderator')
def commandCircled(args):
    args.chat.send(textformat.asciiToCircled(args.message.query))
    return True

@feature('textconvert')
@min_args(2)
@permission('moderator')
def commandSmallCaps(args):
    args.chat.send(textformat.asciiToSmallCaps(args.message.query))
    return True

@feature('textconvert')
@min_args(2)
@permission('moderator')
def commandUpsideDown(args):
    args.chat.send(textformat.asciiToUpsideDown(args.message.query))
    return True

@feature('textconvert')
@min_args(2)
@permission('moderator')
def commandSerifBold(args):
    args.chat.send(textformat.asciiToSerifBold(args.message.query))
    return True

@feature('textconvert')
@min_args(2)
@permission('moderator')
def commandSerifItalic(args):
    args.chat.send(textformat.asciiToSerifItalic(args.message.query))
    return True

@feature('textconvert')
@min_args(2)
@permission('moderator')
def commandSerifBoldItalic(args):
    args.chat.send(textformat.asciiToSerifBoldItalic(args.message.query))
    return True

@feature('textconvert')
@min_args(2)
@permission('moderator')
def commandSanSerif(args):
    args.chat.send(textformat.asciiToSanSerif(args.message.query))
    return True

@feature('textconvert')
@min_args(2)
@permission('moderator')
def commandSanSerifBold(args):
    args.chat.send(textformat.asciiToSanSerifBold(args.message.query))
    return True

@feature('textconvert')
@min_args(2)
@permission('moderator')
def commandSanSerifItalic(args):
    args.chat.send(textformat.asciiToSanSerifItalic(args.message.query))
    return True

@feature('textconvert')
@min_args(2)
@permission('moderator')
def commandSanSerifBoldItalic(args):
    args.chat.send(textformat.asciiToSanSerifBoldItalic(args.message.query))
    return True

@feature('textconvert')
@min_args(2)
@permission('moderator')
def commandScript(args):
    args.chat.send(textformat.asciiToScript(args.message.query))
    return True

@feature('textconvert')
@min_args(2)
@permission('moderator')
def commandScriptBold(args):
    args.chat.send(textformat.asciiToScriptBold(args.message.query))
    return True

@feature('textconvert')
@min_args(2)
@permission('moderator')
def commandFraktur(args):
    args.chat.send(textformat.asciiToFraktur(args.message.query))
    return True

@feature('textconvert')
@min_args(2)
@permission('moderator')
def commandFrakturBold(args):
    args.chat.send(textformat.asciiToFrakturBold(args.message.query))
    return True

@feature('textconvert')
@min_args(2)
@permission('moderator')
def commandMonospace(args):
    args.chat.send(textformat.asciiToMonospace(args.message.query))
    return True

@feature('textconvert')
@min_args(2)
@permission('moderator')
def commandDoubleStruck(args):
    args.chat.send(textformat.asciiToDoubleStruck(args.message.query))
    return True
