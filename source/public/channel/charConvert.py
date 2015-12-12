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
