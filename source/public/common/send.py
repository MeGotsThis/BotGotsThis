def whisper(nick):
    return lambda m, p=1: ircbot.irc.messaging.queueWhisper(nick, m, p)

def channel(channel):
    return channel.sendMessage
