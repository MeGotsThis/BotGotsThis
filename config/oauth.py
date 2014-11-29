import database.factory
import json

def getOAuthToken(broadcaster):
    if broadcaster is None:
        return None
    
    if broadcaster[0] == '#':
        broadcaster = broadcaster[1:]
    with database.factory.getDatabase() as db:
        return db.getOAuthToken(broadcaster)
