﻿from lists.manage import methods

def botManageBot(db, send, nick, message):
    params = db, send, nick, message
    
    m = tokens[1].lower()
    if m in methods and methods[m]:
        return methods[m](*params)
    return False
