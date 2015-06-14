import botcommands.channel
import botcommands.exit
import ircbot.irc

def sendMessage(nick):
    return lambda m, p=1: ircbot.irc.messaging.queueWhisper(nick, m, p)

def commandHello(nick, message, msgParts, permissions):
    ircbot.irc.messaging.queueWhisper(nick, 'Hello Kappa')
    return True

def commandExit(nick, message, msgParts, permissions):
    botcommands.exit.botExit(sendMessage(nick))
    return True

def commandSay(nick, message, msgParts, permissions):
    msgParts = message.split(None, 2)
    if msgParts[1][0] != '#':
        msgParts[1] = '#' + msgParts[1]
    if msgParts[1] in ircbot.irc.channels:
        botcommands.channel.botSay(msgParts[1], msgParts[2])
    return True

def commandJoin(nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False

    chan = msgParts[1].lower()
    if chan[0] != '#':
        chan = '#' + chan
    
    botcommands.channel.botJoin(chan, sendMessage(nick))
    return True

def commandPart(nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    chan = msgParts[1].lower()
    if chan[0] != '#':
        chan = '#' + chan
    botcommands.channel.botPart(chan, sendMessage(nick))
    return True

def commandEmptyAll(nick, message, msgParts, permissions):
    botcommands.channel.botEmptyAll(sendMessage(nick))
    return True

def commandEmpty(nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    if msgParts[1][0] != '#':
        msgParts[1] = '#' + msgParts[1].lower()
    botcommands.channel.botEmpty(msgParts[1], sendMessage(nick))
    return True

