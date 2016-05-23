from lists.feature import features

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

def botFeature(db, channel, message, send):
    if len(message) < 2:
        return False
    
    action = ''
    if len(message) >= 3:
        action = message.lower[2]
    
    if message.lower[1] not in features or features[message.lower[1]] is None:
        send('Unrecognized feature: ' + message.lower[1])
        return True
    
    if action not in enable and action not in disable:
        msg = 'Unrecognized second parameter: ' + action
        send(msg)
        return True
    
    hasFeature = db.hasFeature(channel, message.lower[1])
    if not hasFeature and action in enable:
        db.addFeature(channel, message.lower[1])
    if hasFeature and action in disable:
        db.removeFeature(channel, message.lower[1])
    
    msg = None
    if hasFeature:
        if action in enable:
            msg = 'The feature ' + features[message.lower[1]]
            msg += ' has already been enabled in ' + channel
        if action in disable:
            msg = 'The feature ' + features[message.lower[1]] + ' has been '
            msg += 'disabled in ' + channel
    else:
        if action in enable:
            msg = 'The feature ' + features[message.lower[1]] + ' has been '
            msg += 'enabled in ' + channel
        if action in disable:
            msg = 'The feature ' + features[message.lower[1]] + ' was not '
            msg += 'enabled in ' + channel
    send(msg)
    return True
