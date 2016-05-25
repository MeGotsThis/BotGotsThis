from ..library import charConvert

def commandFull(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(charConvert.asciiToFullWidth(args.message.query))
    return True

def commandParenthesized(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(charConvert.asciiToParenthesized(args.message.query))
    return True

def commandCircled(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(charConvert.asciiToCircled(args.message.query))
    return True

def commandSmallCaps(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(charConvert.asciiToSmallCaps(args.message.query))
    return True

def commandUpsideDown(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(charConvert.asciiToUpsideDown(args.message.query))
    return True

def commandSerifBold(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(charConvert.asciiToSerifBold(args.message.query))
    return True

def commandSerifItalic(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(charConvert.asciiToSerifItalic(args.message.query))
    return True

def commandSerifBoldItalic(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    msg = charConvert.asciiToSerifBoldItalic(args.message.query)
    args.chat.sendMessage(msg)
    return True

def commandSanSerif(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(charConvert.asciiToSanSerif(args.message.query))
    return True

def commandSanSerifBold(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(charConvert.asciiToSanSerifBold(args.message.query))
    return True

def commandSanSerifItalic(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    msg = charConvert.asciiToSanSerifItalic(args.message.query)
    args.chat.sendMessage(msg)
    return True

def commandSanSerifBoldItalic(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    msg = charConvert.asciiToSanSerifBoldItalic(args.message.query)
    args.chat.sendMessage(msg)
    return True

def commandScript(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(charConvert.asciiToScript(args.message.query))
    return True

def commandScriptBold(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(charConvert.asciiToScriptBold(args.message.query))
    return True

def commandFraktur(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(charConvert.asciiToFraktur(args.message.query))
    return True

def commandFrakturBold(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(charConvert.asciiToFrakturBold(args.message.query))
    return True

def commandMonospace(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(charConvert.asciiToMonospace(args.message.query))
    return True

def commandDoubleStruck(args):
    if not args.database.hasFeature(args.chat.channel, 'textconvert'):
        return False
    
    if len(args.message) < 2:
        return False
    args.chat.sendMessage(charConvert.asciiToDoubleStruck(args.message.query))
    return True
