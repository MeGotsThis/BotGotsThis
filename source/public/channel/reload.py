from ..common import reload

def commandReload(channelData, nick, message, msgParts, permissions):
    reload.botReload(channelData.sendMessage, nick, message, msgParts,
                     permissions)
    return True

def commandReloadCommands(channelData, nick, message, msgParts, permissions):
    reload.botReloadCommands(channelData.sendMessage, nick, message, msgParts,
                             permissions)
    return True

def commandReloadConfig(channelData, nick, message, msgParts, permissions):
    reload.botReloadConfig(channelData.sendMessage, nick, message, msgParts,
                           permissions)
    return True
