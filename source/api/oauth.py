from typing import Optional, cast
from .. import database as databaseM


async def token(broadcaster: str, *,
          database: Optional[databaseM.DatabaseOAuth]=None) -> Optional[str]:
    if not isinstance(broadcaster, str):
        raise TypeError()
    if database is None:
        db: databaseM.Database
        async with await databaseM.get_database(databaseM.Schema.OAuth) as db:
            database_ = cast(databaseM.DatabaseOAuth, db)
            return await token(broadcaster, database=database_)
    if not isinstance(database, databaseM.DatabaseOAuth):
        raise TypeError()
    return await database.getOAuthToken(broadcaster)
