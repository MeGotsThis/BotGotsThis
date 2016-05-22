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

def botFeature(db, channel, tokens, send):
    if len(tokens) < 2:
        return False
    
    if len(tokens) < 3:
        tokens.append('')
    
    tokens[1] = tokens[1].lower()
    if tokens[1] not in features or features[tokens[1]] is None:
        send('Unrecognized feature: ' + tokens[1])
        return True
    
    if tokens[2] not in enable and tokens[2] not in disable:
        msg = 'Unrecognized second parameter: ' + tokens[2]
        send(msg)
        return True
    
    hasFeature = db.hasFeature(channel, tokens[1])
    if not hasFeature and tokens[2] in enable:
        db.addFeature(channel, tokens[1])
    if hasFeature and tokens[2] in disable:
        db.removeFeature(channel, tokens[1])
    
    msg = None
    if hasFeature:
        if tokens[2] in enable:
            msg = 'The feature ' + features[tokens[1]]
            msg += ' has already been enabled in ' + channel
        if tokens[2] in disable:
            msg = 'The feature ' + features[tokens[1]] + ' has been '
            msg += 'disabled in ' + channel
    else:
        if tokens[2] in enable:
            msg = 'The feature ' + features[tokens[1]] + ' has been '
            msg += 'enabled in ' + channel
        if tokens[2] in disable:
            msg = 'The feature ' + features[tokens[1]] + ' was not '
            msg += 'enabled in ' + channel
    send(msg)
    return True
