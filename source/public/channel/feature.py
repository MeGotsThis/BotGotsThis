from ..common import feature, send

def commandFeature(db, channel, nick, message, msgParts, permissions):
    return feature.botFeature(db, channel.channel, msgParts,
                              send.channel(channel))
