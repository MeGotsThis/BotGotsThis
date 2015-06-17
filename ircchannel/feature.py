import botcommands.feature

def commandFeature(channelData, nick, message, msgParts, permissions):
    return botcommands.feature.botFeature(
        channelData.channel[1:], msgParts, channelData.sendMessage)
