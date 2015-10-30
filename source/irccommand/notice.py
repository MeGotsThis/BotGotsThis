import bot.error

def parse(channelData, nick, message):
    if message == 'Login unsuccessful':
        raise bot.error.LoginUnsuccessfulException()
