from ..common import reload, send

def commandReload(db, channel, nick, message, msgParts, permissions, now):
    reload.botReload(send.channel(channel))
    return True

def commandReloadCommands(db, channel, nick, message, msgParts, permissions,
                          now):
    reload.botReloadCommands(send.channel(channel))
    return True

def commandReloadConfig(db, channel, nick, message, msgParts, permissions,
                        now):
    reload.botReloadConfig(send.channel(channel))
    return True
