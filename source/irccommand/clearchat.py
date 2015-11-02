from bot import config, globals

def parse(channel, nick):
    if nick == config.botnick:
        channel.isMod = False
        globals.messaging.clearQueue(channel.channel)
