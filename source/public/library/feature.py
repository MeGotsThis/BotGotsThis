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
    
    msg = ''
    if hasFeature:
        if action in enable:
            msg = 'The feature {feature} has already been enabled in {channel}'
        if action in disable:
            msg = 'The feature {feature} has been disabled in {channel}'
    else:
        if action in enable:
            msg = 'The feature {feature} has been enabled in {channel}'
        if action in disable:
            msg = 'The feature {feature} was not enabled in {channel}'
    send(msg.format(feature=features[message.lower[1]], channel=channel))
    return True
