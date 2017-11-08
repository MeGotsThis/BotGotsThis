from typing import Optional
from ..database import DatabaseOAuth


async def token(broadcaster: str, *,
                database: Optional[DatabaseOAuth]=None
                ) -> Optional[str]:
    if not isinstance(broadcaster, str):
        raise TypeError()
    if database is None:
        db: DatabaseOAuth
        async with DatabaseOAuth.acquire() as db:
            return await token(broadcaster, database=db)
    if not isinstance(database, DatabaseOAuth):
        raise TypeError()
    return await database.getOAuthToken(broadcaster)
