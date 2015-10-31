from ..common import reload

def commandReload(db, channel, nick, message, msgParts, permissions):
    reload.botReload(channel.sendMessage, nick, message, msgParts, permissions)
    return True

def commandReloadCommands(db, channel, nick, message, msgParts, permissions):
    reload.botReloadCommands(channel.sendMessage, nick, message, msgParts,
                             permissions)
    return True

def commandReloadConfig(db, channel, nick, message, msgParts, permissions):
    reload.botReloadConfig(channel.sendMessage, nick, message, msgParts,
                           permissions)
    return True
