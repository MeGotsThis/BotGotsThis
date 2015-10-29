from ..common import feature

def commandFeature(channelData, nick, message, msgParts, permissions):
    return feature.botFeature(
        channelData.channel[1:], msgParts, channelData.sendMessage)
