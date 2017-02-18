from typing import Optional
from ..database import DatabaseBase, factory


def token(broadcaster: str, *,
          database: Optional[DatabaseBase]=None) -> Optional[str]:
    if not isinstance(broadcaster, str):
        raise TypeError()
    if database is None:
        db: DatabaseBase
        with factory.getDatabase() as db:
            return token(broadcaster, database=db)
    if not isinstance(database, DatabaseBase):
        raise TypeError()
    return database.getOAuthToken(broadcaster)
