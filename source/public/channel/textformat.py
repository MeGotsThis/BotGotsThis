from ..library import textformat
from ..library.chat import feature, permission

@feature('textconvert')
@permission('moderator')
def commandFull(args):
    if len(args.message) < 2:
        return False
    args.chat.send(textformat.asciiToFullWidth(args.message.query))
    return True

@feature('textconvert')
@permission('moderator')
def commandParenthesized(args):
    if len(args.message) < 2:
        return False
    args.chat.send(textformat.asciiToParenthesized(args.message.query))
    return True

@feature('textconvert')
@permission('moderator')
def commandCircled(args):
    if len(args.message) < 2:
        return False
    args.chat.send(textformat.asciiToCircled(args.message.query))
    return True

@feature('textconvert')
@permission('moderator')
def commandSmallCaps(args):
    if len(args.message) < 2:
        return False
    args.chat.send(textformat.asciiToSmallCaps(args.message.query))
    return True

@feature('textconvert')
@permission('moderator')
def commandUpsideDown(args):
    if len(args.message) < 2:
        return False
    args.chat.send(textformat.asciiToUpsideDown(args.message.query))
    return True

@feature('textconvert')
@permission('moderator')
def commandSerifBold(args):
    if len(args.message) < 2:
        return False
    args.chat.send(textformat.asciiToSerifBold(args.message.query))
    return True

@feature('textconvert')
@permission('moderator')
def commandSerifItalic(args):
    if len(args.message) < 2:
        return False
    args.chat.send(textformat.asciiToSerifItalic(args.message.query))
    return True

@feature('textconvert')
@permission('moderator')
def commandSerifBoldItalic(args):
    if len(args.message) < 2:
        return False
    args.chat.send(textformat.asciiToSerifBoldItalic(args.message.query))
    return True

@feature('textconvert')
@permission('moderator')
def commandSanSerif(args):
    if len(args.message) < 2:
        return False
    args.chat.send(textformat.asciiToSanSerif(args.message.query))
    return True

@feature('textconvert')
@permission('moderator')
def commandSanSerifBold(args):
    if len(args.message) < 2:
        return False
    args.chat.send(textformat.asciiToSanSerifBold(args.message.query))
    return True

@feature('textconvert')
@permission('moderator')
def commandSanSerifItalic(args):
    if len(args.message) < 2:
        return False
    args.chat.send(textformat.asciiToSanSerifItalic(args.message.query))
    return True

@feature('textconvert')
@permission('moderator')
def commandSanSerifBoldItalic(args):
    if len(args.message) < 2:
        return False
    args.chat.send(textformat.asciiToSanSerifBoldItalic(args.message.query))
    return True

@feature('textconvert')
@permission('moderator')
def commandScript(args):
    if len(args.message) < 2:
        return False
    args.chat.send(textformat.asciiToScript(args.message.query))
    return True

@feature('textconvert')
@permission('moderator')
def commandScriptBold(args):
    if len(args.message) < 2:
        return False
    args.chat.send(textformat.asciiToScriptBold(args.message.query))
    return True

@feature('textconvert')
@permission('moderator')
def commandFraktur(args):
    if len(args.message) < 2:
        return False
    args.chat.send(textformat.asciiToFraktur(args.message.query))
    return True

@feature('textconvert')
@permission('moderator')
def commandFrakturBold(args):
    if len(args.message) < 2:
        return False
    args.chat.send(textformat.asciiToFrakturBold(args.message.query))
    return True

@feature('textconvert')
@permission('moderator')
def commandMonospace(args):
    if len(args.message) < 2:
        return False
    args.chat.send(textformat.asciiToMonospace(args.message.query))
    return True

@feature('textconvert')
@permission('moderator')
def commandDoubleStruck(args):
    if len(args.message) < 2:
        return False
    args.chat.send(textformat.asciiToDoubleStruck(args.message.query))
    return True
