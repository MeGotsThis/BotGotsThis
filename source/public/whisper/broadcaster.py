import botcommands.broadcaster
import ircbot.irc

def sendMessage(nick):
    return lambda m, p=1: ircbot.irc.messaging.queueWhisper(nick, m, p)

def commandCome(nick, message, msgParts, permissions):
    botcommands.broadcaster.botCome(nick, sendMessage(nick))
    return True

def commandLeave(nick, message, msgParts, permissions):
    return botcommands.broadcaster.botLeave('#' + nick, sendMessage(nick))

def commandEmpty(nick, message, msgParts, permissions):
    botcommands.broadcaster.botEmpty('#' + nick, sendMessage(nick))
    return True

def commandAutoJoin(nick, message, msgParts, permissions):
    botcommands.broadcaster.botAutoJoin(
        nick, sendMessage(nick), msgParts)
    return True

