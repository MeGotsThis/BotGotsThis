import botcommands.feature
import ircbot.irc

def sendMessage(nick):
    return lambda m, p=1: ircbot.irc.messaging.queueWhisper(nick, m, p)

def commandFeature(nick, message, msgParts, permissions):
    return botcommands.feature.botFeature(nick, msgParts, sendMessage(nick))
