from ..common import feature, send

def commandFeature(db, chat, tags, nick, message, tokens, permissions, now):
    return feature.botFeature(db, chat.channel, tokens, send.channel(chat))
