from ...database.factory import getDatabase
try:
    from lists.private import feature as privateFeature
except:
    from lists.private.default import feature as privateFeature


features = {
    'textconvert': 'Text Character Conversion',
    'modpyramid': 'Mods Using !pyramid',
    'modwall': 'Mods Using !wall',
    'nocustom': 'Disable Custom Commands',
    'nourlredirect': 'Ban URL Redirect (user has no follows)',
    }
features = dict(list(features.items()) + list(privateFeature.features.items()))

enable = {
    '',
    'enable',
    'yes',
    '1',
    }
disable = {
    'disable',
    'no',
    '0',
    }

def botFeature(channel, msgParts, sendMessage):
    if len(msgParts) < 2:
        return False
    
    if len(msgParts) < 3:
        msgParts.append('')
    
    msgParts[1] = msgParts[1].lower()
    if msgParts[1] not in features:
        sendMessage('Unrecognized feature: ' + msgParts[1])
        return True
    
    if msgParts[2] not in enable and msgParts[2] not in disable:
        msg = 'Unrecognized second parameter: ' + msgParts[2]
        sendMessage(msg)
        return True
    
    with getDatabase() as db:
        hasFeature = db.hasFeature(channel, msgParts[1])
        if not hasFeature and msgParts[2] in enable:
            db.addFeature(channel, msgParts[1])
        if hasFeature and msgParts[2] in disable:
            db.removeFeature(channel, msgParts[1])
    msg = None
    if hasFeature:
        if msgParts[2] in enable:
            msg = 'The feature ' + features[msgParts[1]]
            msg += ' has already been enabled in ' + channel
        if msgParts[2] in disable:
            msg = 'The feature ' + features[msgParts[1]] + ' has been '
            msg += 'disabled in ' + channel
    else:
        if msgParts[2] in enable:
            msg = 'The feature ' + features[msgParts[1]] + ' has been '
            msg += 'enabled in ' + channel
        if msgParts[2] in disable:
            msg = 'The feature ' + features[msgParts[1]] + ' was not '
            msg += 'enabled in ' + channel
    sendMessage(msg)
    return True
