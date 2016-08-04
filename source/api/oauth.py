from typing import Optional
from ..database import DatabaseBase, factory


def token(broadcaster: str, *,
          database: Optional[DatabaseBase]=None) -> Optional[str]:
    if not isinstance(broadcaster, str):
        raise TypeError()
    if database is None:
        with factory.getDatabase() as database:  # --type: DatabaseBase
            return token(broadcaster, database=database)
    if not isinstance(database, DatabaseBase):
        raise TypeError()
    return database.getOAuthToken(broadcaster)
