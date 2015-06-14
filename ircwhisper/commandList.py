import ircwhisper.owner
try:
    import privatewhisper.commandList as commandList
except:
    import privatewhisper.default.commandList as commandList

commands = {
    '!hello': (ircwhisper.owner.commandHello, 'owner'),
    }

commands = dict(list(commands.items()) + list(commandList.commands.items()))
