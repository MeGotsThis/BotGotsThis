from ..library import textformat
from ..library.chat import permission

@permission('moderator')
def commandFull(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToFullWidth(args.message.query))
    return True

@permission('moderator')
def commandParenthesized(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToParenthesized(args.message.query))
    return True

@permission('moderator')
def commandCircled(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToCircled(args.message.query))
    return True

@permission('moderator')
def commandSmallCaps(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToSmallCaps(args.message.query))
    return True

@permission('moderator')
def commandUpsideDown(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToUpsideDown(args.message.query))
    return True

@permission('moderator')
def commandSerifBold(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToSerifBold(args.message.query))
    return True

@permission('moderator')
def commandSerifItalic(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToSerifItalic(args.message.query))
    return True

@permission('moderator')
def commandSerifBoldItalic(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    msg = textformat.asciiToSerifBoldItalic(args.message.query)
    args.chat.sendMessage(msg)
    return True

@permission('moderator')
def commandSanSerif(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToSanSerif(args.message.query))
    return True

@permission('moderator')
def commandSanSerifBold(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToSanSerifBold(args.message.query))
    return True

@permission('moderator')
def commandSanSerifItalic(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    msg = textformat.asciiToSanSerifItalic(args.message.query)
    args.chat.sendMessage(msg)
    return True

@permission('moderator')
def commandSanSerifBoldItalic(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    msg = textformat.asciiToSanSerifBoldItalic(args.message.query)
    args.chat.sendMessage(msg)
    return True

@permission('moderator')
def commandScript(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToScript(args.message.query))
    return True

@permission('moderator')
def commandScriptBold(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToScriptBold(args.message.query))
    return True

@permission('moderator')
def commandFraktur(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToFraktur(args.message.query))
    return True

@permission('moderator')
def commandFrakturBold(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToFrakturBold(args.message.query))
    return True

@permission('moderator')
def commandMonospace(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToMonospace(args.message.query))
    return True

@permission('moderator')
def commandDoubleStruck(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToDoubleStruck(args.message.query))
    return True
