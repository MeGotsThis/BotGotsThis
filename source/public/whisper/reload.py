import botcommands.reload
import ircbot.irc

def sendMessage(nick):
    return lambda m, p=1: ircbot.irc.messaging.queueWhisper(nick, m, p)

def commandReload(nick, message, msgParts, permissions):
    botcommands.reload.botReload(sendMessage(nick), nick,
                                 message, msgParts, permissions)
    return True

def commandReloadCommands(nick, message, msgParts, permissions):
    botcommands.reload.botReloadCommands(sendMessage(nick), nick,
                                         message, msgParts, permissions)
    return True

def commandReloadConfig(nick, message, msgParts, permissions):
    botcommands.reload.botReloadConfig(sendMessage(nick), nick,
                                       message, msgParts, permissions)
    return True
