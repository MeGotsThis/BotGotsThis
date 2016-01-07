from ..common import charConvert

def commandFull(db, channel, nick, message, msgParts, permissions, now):
    if not db.hasFeature(channel.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    channel.sendMessage(charConvert.asciiToFullWidth(parts[1]))
    return True

def commandParenthesized(db, channel, nick, message, msgParts, permissions,
                         now):
    if not db.hasFeature(channel.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    channel.sendMessage(charConvert.asciiToParenthesized(parts[1]))
    return True

def commandCircled(db, channel, nick, message, msgParts, permissions, now):
    if not db.hasFeature(channel.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    channel.sendMessage(charConvert.asciiToCircled(parts[1]))
    return True

def commandSmallCaps(db, channel, nick, message, msgParts, permissions, now):
    if not db.hasFeature(channel.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    channel.sendMessage(charConvert.asciiToSmallCaps(parts[1]))
    return True

def commandUpsideDown(db, channel, nick, message, msgParts, permissions, now):
    if not db.hasFeature(channel.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    channel.sendMessage(charConvert.asciiToUpsideDown(parts[1]))
    return True

def commandSerifBold(db, channel, nick, message, msgParts, permissions, now):
    if not db.hasFeature(channel.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    channel.sendMessage(charConvert.asciiToSerifBold(parts[1]))
    return True

def commandSerifItalic(db, channel, nick, message, msgParts, permissions, now):
    if not db.hasFeature(channel.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    channel.sendMessage(charConvert.asciiToSerifItalic(parts[1]))
    return True

def commandSerifBoldItalic(db, channel, nick, message, msgParts, permissions,
                           now):
    if not db.hasFeature(channel.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    channel.sendMessage(charConvert.asciiToSerifBoldItalic(parts[1]))
    return True

def commandSanSerif(db, channel, nick, message, msgParts, permissions, now):
    if not db.hasFeature(channel.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    channel.sendMessage(charConvert.asciiToSanSerif(parts[1]))
    return True

def commandSanSerifBold(db, channel, nick, message, msgParts, permissions,
                        now):
    if not db.hasFeature(channel.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    channel.sendMessage(charConvert.asciiToSanSerifBold(parts[1]))
    return True

def commandSanSerifItalic(db, channel, nick, message, msgParts, permissions,
                          now):
    if not db.hasFeature(channel.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    channel.sendMessage(charConvert.asciiToSanSerifItalic(parts[1]))
    return True

def commandSanSerifBoldItalic(db, channel, nick, message, msgParts,
                              permissions, now):
    if not db.hasFeature(channel.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    channel.sendMessage(charConvert.asciiToSanSerifBoldItalic(parts[1]))
    return True

def commandScript(db, channel, nick, message, msgParts, permissions, now):
    if not db.hasFeature(channel.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    channel.sendMessage(charConvert.asciiToScript(parts[1]))
    return True

def commandScriptBold(db, channel, nick, message, msgParts, permissions, now):
    if not db.hasFeature(channel.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    channel.sendMessage(charConvert.asciiToScriptBold(parts[1]))
    return True

def commandFraktur(db, channel, nick, message, msgParts, permissions, now):
    if not db.hasFeature(channel.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    channel.sendMessage(charConvert.asciiToFraktur(parts[1]))
    return True

def commandFrakturBold(db, channel, nick, message, msgParts, permissions, now):
    if not db.hasFeature(channel.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    channel.sendMessage(charConvert.asciiToFrakturBold(parts[1]))
    return True

def commandMonospace(db, channel, nick, message, msgParts, permissions, now):
    if not db.hasFeature(channel.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    channel.sendMessage(charConvert.asciiToMonospace(parts[1]))
    return True

def commandDoubleStruck(db, channel, nick, message, msgParts, permissions,
                        now):
    if not db.hasFeature(channel.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    channel.sendMessage(charConvert.asciiToDoubleStruck(parts[1]))
    return True
