from ..common import feature

def commandFeature(db, channel, nick, message, msgParts, permissions):
    return feature.botFeature(db, channel.channel, msgParts,
                              send.channel(channel))
