from ..common import reload, send

def commandReload(db, chat, tags, nick, message, msgParts, permissions, now):
    reload.botReload(send.channel(chat))
    return True

def commandReloadCommands(db, chat, tags, nick, message, msgParts, permissions,
                          now):
    reload.botReloadCommands(send.channel(chat))
    return True

def commandReloadConfig(db, chat, tags, nick, message, msgParts, permissions,
                        now):
    reload.botReloadConfig(send.channel(chat))
    return True
