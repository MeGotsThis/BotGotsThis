from ..library import reload, send

def commandReload(args):
    reload.botReload(send.channel(args.chat))
    return True

def commandReloadCommands(args):
    reload.botReloadCommands(send.channel(args.chat))
    return True

def commandReloadConfig(args):
    reload.botReloadConfig(send.channel(args.chat))
    return True
