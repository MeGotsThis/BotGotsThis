def parse(channelData, message):
    if message.startswith('The moderators of this room are: '):
        l = len('The moderators of this room are: ')
        mods = message[l:]
        for mod in mods.split(', '):
            mod = str(mod)
            channelData.addMod(mod)
    if message.startswith('SPECIALUSER'):
        user, usertype = message.split(' ')[1:3]
        user = str(user)
        usertype = str(usertype)
        if usertype == 'staff':
            channelData.addTwitchStaff(user)
        if usertype == 'admin':
            channelData.addTwitchAdmin(user)
        if usertype == 'global_mod':
            channelData.addGlobalMod(user)
        if usertype == 'subscriber':
            channelData.addSubscriber(user)
        if usertype == 'turbo':
            channelData.addTurboUser(user)
