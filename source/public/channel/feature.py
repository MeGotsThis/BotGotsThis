from ..common import feature, send

def commandFeature(db, chat, tags, nick, message, msgParts, permissions, now):
    return feature.botFeature(db, chat.channel, msgParts,
                              send.channel(chat))
