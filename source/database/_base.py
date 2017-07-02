import aioodbc
import aioodbc.cursor
import pyodbc

from typing import Optional


class Database:
    def __init__(self,
                 connectionString: str,
                 **kwargs) -> None:
        self._connectionString: str = connectionString
        self._connection: Optional[aioodbc.Connection] = None
        self._driver: Optional[str] = None

    @property
    def connection(self) -> Optional[aioodbc.Connection]:
        return self._connection

    async def connect(self) -> None:
        self._connection = await aioodbc.connect(dsn=self._connectionString)
        driver: str = await self._connection.getinfo(pyodbc.SQL_DRIVER_NAME)
        self._driver = driver.lower()
        if self.isPostgres:
            cursor: aioodbc.cursor.Cursor
            async with await self.cursor() as cursor:
                await cursor.execute("SET TIME ZONE 'UTC'")

    async def close(self) -> None:
        if self.connection is not None:
            await self.connection.close()

    async def __aenter__(self) -> 'Database':
        await self.connect()
        return self

    async def __aexit__(self, type, value, traceback) -> None:
        await self.close()

    @property
    def isSqlite(self):
        return 'sqlite' in self._driver

    @property
    def isPostgres(self):
        return 'psql' in self._driver

    async def cursor(self) -> aioodbc.cursor.Cursor:
        return await self.connection.cursor()

    async def commit(self) -> None:
        await self.connection.commit()
