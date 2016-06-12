from typing import Optional
from ..database import DatabaseBase
from ..database.factory import getDatabase


def getOAuthToken(broadcaster: str) -> Optional[str]:
    if broadcaster is None:
        return None
    
    with getDatabase() as db:  # --type: DatabaseBase
        return db.getOAuthToken(broadcaster)


def getOAuthTokenWithDB(db: DatabaseBase,
                        broadcaster: str) -> Optional[str]:
    if broadcaster is None:
        return None
    
    return db.getOAuthToken(broadcaster)
