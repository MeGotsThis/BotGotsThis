import ircwhisper.owner
import ircwhisper.reload
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
    '!managebot': (ircwhisper.owner.commandManageBot, 'owner'),
    '!reload': (ircwhisper.reload.commandReload, 'owner'),
    '!reloadcommands': (ircwhisper.reload.commandReloadCommands, 'owner'),
    '!reloadconfig': (ircwhisper.reload.commandReloadConfig, 'owner'),
    }

commands = dict(list(commands.items()) + list(commandList.commands.items()))
