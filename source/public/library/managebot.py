from lists.manage import methods

def botManageBot(database, send, nick, message):
    params = database, send, nick, message
    
    m = message.lower[1]
    if m in methods and methods[m]:
        return methods[m](*params)
    return False
