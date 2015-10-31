from ..common import reload, send

def commandReload(db, channel, nick, message, msgParts, permissions):
    reload.botReload(send.channel(channel), nick, message, msgParts,
                     permissions)
    return True

def commandReloadCommands(db, channel, nick, message, msgParts, permissions):
    reload.botReloadCommands(send.channel(channel), nick, message, msgParts,
                             permissions)
    return True

def commandReloadConfig(db, channel, nick, message, msgParts, permissions):
    reload.botReloadConfig(send.channel(channel), nick, message, msgParts,
                           permissions)
    return True
