from ..library import textformat

def commandFull(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToFullWidth(args.message.query))
    return True

def commandParenthesized(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToParenthesized(args.message.query))
    return True

def commandCircled(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToCircled(args.message.query))
    return True

def commandSmallCaps(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToSmallCaps(args.message.query))
    return True

def commandUpsideDown(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToUpsideDown(args.message.query))
    return True

def commandSerifBold(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToSerifBold(args.message.query))
    return True

def commandSerifItalic(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToSerifItalic(args.message.query))
    return True

def commandSerifBoldItalic(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    msg = textformat.asciiToSerifBoldItalic(args.message.query)
    args.chat.sendMessage(msg)
    return True

def commandSanSerif(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToSanSerif(args.message.query))
    return True

def commandSanSerifBold(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToSanSerifBold(args.message.query))
    return True

def commandSanSerifItalic(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    msg = textformat.asciiToSanSerifItalic(args.message.query)
    args.chat.sendMessage(msg)
    return True

def commandSanSerifBoldItalic(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    msg = textformat.asciiToSanSerifBoldItalic(args.message.query)
    args.chat.sendMessage(msg)
    return True

def commandScript(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToScript(args.message.query))
    return True

def commandScriptBold(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToScriptBold(args.message.query))
    return True

def commandFraktur(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToFraktur(args.message.query))
    return True

def commandFrakturBold(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToFrakturBold(args.message.query))
    return True

def commandMonospace(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToMonospace(args.message.query))
    return True

def commandDoubleStruck(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(textformat.asciiToDoubleStruck(args.message.query))
    return True
