import botcommands.reload

def commandReload(channelData, nick, message, msgParts, permissions):
    botcommands.reload.botReload(channelData.sendMessage, nick,
                                 message, msgParts, permissions)
    return True

def commandReloadCommands(channelData, nick, message, msgParts, permissions):
    botcommands.reload.botReloadCommands(channelData.sendMessage, nick,
                                         message, msgParts, permissions)
    return True

def commandReloadConfig(channelData, nick, message, msgParts, permissions):
    botcommands.reload.botReloadConfig(channelData.sendMessage, nick,
                                       message, msgParts, permissions)
    return True
