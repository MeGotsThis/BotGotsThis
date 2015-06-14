import ircwhisper.owner
try:
    import privatewhisper.commandList as commandList
except:
    import privatewhisper.default.commandList as commandList

commands = {
    '!hello': (ircwhisper.owner.commandHello, 'owner'),
    '!exit': (ircwhisper.owner.commandExit, 'owner'),
    '!say': (ircwhisper.owner.commandSay, 'owner'),
    '!join': (ircwhisper.owner.commandJoin, 'admin'),
    '!part': (ircwhisper.owner.commandPart, 'admin'),
    '!emptychat': (ircwhisper.owner.commandEmpty, 'admin'),
    '!emptyall': (ircwhisper.owner.commandEmptyAll, 'admin'),
    }

commands = dict(list(commands.items()) + list(commandList.commands.items()))
