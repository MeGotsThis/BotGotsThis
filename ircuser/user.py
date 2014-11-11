def parse(channelThread, nick, message):
    if nick == 'jtv':
        if message.startswith('The moderators of this room are: '):
            l = len('The moderators of this room are: ')
            mods = message[l:]
            for mod in mods.split(', '):
                channelThread.mods.append(mod)
        if message.startswith('SPECIALUSER'):
            _, user, type = message.split(' ')
            if type == 'staff' and user not in channelThread.twitchStaff:
                channelThread.twitchStaff.append(user)
            if type == 'admin' and user not in channelThread.twitchAdmin:
                channelThread.twitchAdmin.append(user)
