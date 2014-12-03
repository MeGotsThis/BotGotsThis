import ircbot.socket

def parse(channelData, nick, message):
    if message == 'Login unsuccessful':
        raise ircbot.socket.LoginUnsuccessfulException()
