from ..common import charConvert

def commandFull(db, chat, tags, nick, message, tokens, permissions, now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    chat.sendMessage(charConvert.asciiToFullWidth(parts[1]))
    return True

def commandParenthesized(db, chat, tags, nick, message, tokens, permissions,
                         now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    chat.sendMessage(charConvert.asciiToParenthesized(parts[1]))
    return True

def commandCircled(db, chat, tags, nick, message, tokens, permissions, now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    chat.sendMessage(charConvert.asciiToCircled(parts[1]))
    return True

def commandSmallCaps(db, chat, tags, nick, message, tokens, permissions,
                     now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    chat.sendMessage(charConvert.asciiToSmallCaps(parts[1]))
    return True

def commandUpsideDown(db, chat, tags, nick, message, tokens, permissions,
                      now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    chat.sendMessage(charConvert.asciiToUpsideDown(parts[1]))
    return True

def commandSerifBold(db, chat, tags, nick, message, tokens, permissions,
                     now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    chat.sendMessage(charConvert.asciiToSerifBold(parts[1]))
    return True

def commandSerifItalic(db, chat, tags, nick, message, tokens, permissions,
                       now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    chat.sendMessage(charConvert.asciiToSerifItalic(parts[1]))
    return True

def commandSerifBoldItalic(db, chat, tags, nick, message, tokens,
                           permissions, now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    chat.sendMessage(charConvert.asciiToSerifBoldItalic(parts[1]))
    return True

def commandSanSerif(db, chat, tags, nick, message, tokens, permissions, now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    chat.sendMessage(charConvert.asciiToSanSerif(parts[1]))
    return True

def commandSanSerifBold(db, chat, tags, nick, message, tokens, permissions,
                        now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    chat.sendMessage(charConvert.asciiToSanSerifBold(parts[1]))
    return True

def commandSanSerifItalic(db, chat, tags, nick, message, tokens, permissions,
                          now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    chat.sendMessage(charConvert.asciiToSanSerifItalic(parts[1]))
    return True

def commandSanSerifBoldItalic(db, chat, tags, nick, message, tokens,
                              permissions, now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    chat.sendMessage(charConvert.asciiToSanSerifBoldItalic(parts[1]))
    return True

def commandScript(db, chat, tags, nick, message, tokens, permissions, now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    chat.sendMessage(charConvert.asciiToScript(parts[1]))
    return True

def commandScriptBold(db, chat, tags, nick, message, tokens, permissions,
                      now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    chat.sendMessage(charConvert.asciiToScriptBold(parts[1]))
    return True

def commandFraktur(db, chat, tags, nick, message, tokens, permissions, now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    chat.sendMessage(charConvert.asciiToFraktur(parts[1]))
    return True

def commandFrakturBold(db, chat, tags, nick, message, tokens, permissions,
                       now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    chat.sendMessage(charConvert.asciiToFrakturBold(parts[1]))
    return True

def commandMonospace(db, chat, tags, nick, message, tokens, permissions,
                     now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    chat.sendMessage(charConvert.asciiToMonospace(parts[1]))
    return True

def commandDoubleStruck(db, chat, tags, nick, message, tokens, permissions,
                        now):
    if not db.hasFeature(chat.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    chat.sendMessage(charConvert.asciiToDoubleStruck(parts[1]))
    return True
