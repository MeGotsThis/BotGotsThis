import ircbot.ircsocket

def parse(channelData, nick, message):
    if message == 'Login unsuccessful':
        raise ircbot.ircsocket.LoginUnsuccessfulException()
