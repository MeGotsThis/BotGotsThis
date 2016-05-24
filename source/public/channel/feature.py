from ..library import feature, send

def commandFeature(db, chat, tags, nick, message, permissions, now):
    return feature.botFeature(db, chat.channel, message, send.channel(chat))
