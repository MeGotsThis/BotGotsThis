from ..library import charConvert

def commandFull(db, chat, tags, nick, message, permissions, now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    if len(message) < 2:
        return False
    chat.sendMessage(charConvert.asciiToFullWidth(message.query))
    return True

def commandParenthesized(db, chat, tags, nick, message, permissions, now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    if len(message) < 2:
        return False
    chat.sendMessage(charConvert.asciiToParenthesized(message.query))
    return True

def commandCircled(db, chat, tags, nick, message, permissions, now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    if len(message) < 2:
        return False
    chat.sendMessage(charConvert.asciiToCircled(message.query))
    return True

def commandSmallCaps(db, chat, tags, nick, message, permissions, now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    if len(message) < 2:
        return False
    chat.sendMessage(charConvert.asciiToSmallCaps(message.query))
    return True

def commandUpsideDown(db, chat, tags, nick, message, permissions, now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    if len(message) < 2:
        return False
    chat.sendMessage(charConvert.asciiToUpsideDown(message.query))
    return True

def commandSerifBold(db, chat, tags, nick, message, permissions, now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    if len(message) < 2:
        return False
    chat.sendMessage(charConvert.asciiToSerifBold(message.query))
    return True

def commandSerifItalic(db, chat, tags, nick, message, permissions, now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    if len(message) < 2:
        return False
    chat.sendMessage(charConvert.asciiToSerifItalic(message.query))
    return True

def commandSerifBoldItalic(db, chat, tags, nick, message, permissions, now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    if len(message) < 2:
        return False
    chat.sendMessage(charConvert.asciiToSerifBoldItalic(message.query))
    return True

def commandSanSerif(db, chat, tags, nick, message, permissions, now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    if len(message) < 2:
        return False
    chat.sendMessage(charConvert.asciiToSanSerif(message.query))
    return True

def commandSanSerifBold(db, chat, tags, nick, message, permissions, now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    if len(message) < 2:
        return False
    chat.sendMessage(charConvert.asciiToSanSerifBold(message.query))
    return True

def commandSanSerifItalic(db, chat, tags, nick, message, permissions, now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    if len(message) < 2:
        return False
    chat.sendMessage(charConvert.asciiToSanSerifItalic(message.query))
    return True

def commandSanSerifBoldItalic(db, chat, tags, nick, message, permissions, now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    if len(message) < 2:
        return False
    chat.sendMessage(charConvert.asciiToSanSerifBoldItalic(message.query))
    return True

def commandScript(db, chat, tags, nick, message, permissions, now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    if len(message) < 2:
        return False
    chat.sendMessage(charConvert.asciiToScript(message.query))
    return True

def commandScriptBold(db, chat, tags, nick, message, permissions, now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    if len(message) < 2:
        return False
    chat.sendMessage(charConvert.asciiToScriptBold(message.query))
    return True

def commandFraktur(db, chat, tags, nick, message, permissions, now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    if len(message) < 2:
        return False
    chat.sendMessage(charConvert.asciiToFraktur(message.query))
    return True

def commandFrakturBold(db, chat, tags, nick, message, permissions, now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    if len(message) < 2:
        return False
    chat.sendMessage(charConvert.asciiToFrakturBold(message.query))
    return True

def commandMonospace(db, chat, tags, nick, message, permissions, now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    if len(message) < 2:
        return False
    chat.sendMessage(charConvert.asciiToMonospace(message.query))
    return True

def commandDoubleStruck(db, chat, tags, nick, message, permissions, now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    if len(message) < 2:
        return False
    chat.sendMessage(charConvert.asciiToDoubleStruck(message.query))
    return True
