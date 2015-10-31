from ..database.factory import getDatabase
import json

def getOAuthToken(broadcaster):
    if broadcaster is None:
        return None
    
    with getDatabase() as db:
        return db.getOAuthToken(broadcaster)

def getOAuthTokenWithDB(db, broadcaster):
    if broadcaster is None:
        return None
    
    return db.getOAuthToken(broadcaster)
