import ircbot.irc

def parse(channelThread, nick, message):
    if message == 'Login unsuccessful':
        raise ircbot.irc.LoginUnsuccessfulException()
