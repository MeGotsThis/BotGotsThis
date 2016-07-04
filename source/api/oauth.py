from typing import Optional
from ..database import DatabaseBase
from ..database.factory import getDatabase


def token(broadcaster: str, *,
          database: Optional[DatabaseBase]=None) -> Optional[str]:
    if not isinstance(broadcaster, str):
        raise TypeError()
    if database is None:
        with getDatabase() as database:  # --type: DatabaseBase
            return token(broadcaster, database=database)
    if not isinstance(database, DatabaseBase):
        raise TypeError()
    return database.getOAuthToken(broadcaster)
