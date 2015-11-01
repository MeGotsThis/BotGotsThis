from lists.manage import methods

def botManageBot(db, send, nick, message, msgParts):
    params = db, send, nick, message, msgParts
    
    m = msgParts[1].lower()
    if m in methods and methods[m]:
        return methods[m](*params)
    return False
