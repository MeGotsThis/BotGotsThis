def parse(channelThread, nick, message):
    if nick == 'jtv':
        if message.startswith('The moderators of this room are: '):
            l = len('The moderators of this room are: ')
            mods = message[l:]
            for mod in mods.split(', '):
                channelThread.mods.append(mod)