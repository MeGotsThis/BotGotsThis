from ..common import feature

def commandFeature(channelData, nick, message, msgParts, permissions):
    return feature.botFeature(
        channelData.channel, msgParts, channelData.sendMessage)
