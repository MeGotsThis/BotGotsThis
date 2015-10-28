import bot.thread.socket

def parse(channelData, nick, message):
    if message == 'Login unsuccessful':
        raise bot.thread.socket.LoginUnsuccessfulException()
