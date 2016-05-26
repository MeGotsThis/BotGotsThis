from bot.data.argument import ManageBotArgs
from lists.manage import methods

def botManageBot(database, send, nick, message):
    argument = ManageBotArgs(database, send, nick, message)
    
    m = message.lower[1]
    if m in methods and methods[m]:
        return methods[m](argument)
    return False
