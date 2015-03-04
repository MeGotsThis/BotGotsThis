from config import config
import privatechannel.feature
import database.factory
import ircbot.irc

features = {
    'textconvert': 'Text Character Conversion',
    }
features = dict(
    list(features.items()) + list(privatechannel.feature.features.items()))

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

def commandFeature(channelData, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    
    if len(msgParts) < 3:
        msgParts.append('')
    
    msgParts[1] = msgParts[1].lower()
    if msgParts[1] not in features:
        channelData.sendMessage('Unrecognized feature: ' + msgParts[1])
        return True
    
    if msgParts[2] not in enable and msgParts[2] not in disable:
        msg = 'Unrecognized second parameter: ' + msgParts[2]
        channelData.sendMessage(msg)
        return True
    
    with database.factory.getDatabase() as db:
        hasFeature = db.hasFeature(channelData.channel[1:], msgParts[1])
        if not hasFeature and msgParts[2] in enable:
            db.addFeature(channelData.channel[1:], msgParts[1])
        if hasFeature and msgParts[2] in disable:
            db.removeFeature(channelData.channel[1:], msgParts[1])
    msg = None
    if hasFeature:
        if msgParts[2] in enable:
            msg = 'The feature ' + features[msgParts[1]]
            msg += ' has already been enabled'
        if msgParts[2] in disable:
            msg = 'The feature ' + features[msgParts[1]] + ' has been disabled'
    else:
        if msgParts[2] in enable:
            msg = 'The feature ' + features[msgParts[1]] + ' has been enabled'
        if msgParts[2] in disable:
            msg = 'The feature ' + features[msgParts[1]] + ' was not enabled'
    channelData.sendMessage(msg)
    return True
