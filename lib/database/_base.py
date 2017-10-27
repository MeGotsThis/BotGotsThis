import aioodbc
import aioodbc.cursor
import pyodbc

from typing import Optional, Type, TYPE_CHECKING
if TYPE_CHECKING:
    from types import TracebackType  # noqa: F401


class Database:
    def __init__(self,
                 pool: aioodbc.Pool) -> None:
        self._pool: aioodbc.Pool = pool
        self._connection: Optional[aioodbc.Connection] = None
        self._driver: Optional[str] = None

    @property
    def connection(self) -> aioodbc.Connection:
        if self._connection is None:
            raise ConnectionError('Database not connected')
        return self._connection

    async def connect(self) -> None:
        self._connection = await self._pool.acquire()
        driver: str = await self._connection.getinfo(pyodbc.SQL_DRIVER_NAME)
        self._driver = driver.lower()
        if self.isPostgres:
            cursor: aioodbc.cursor.Cursor
            await self.connection.rollback()
            async with await self.cursor() as cursor:
                await cursor.execute("SET TIME ZONE 'UTC'")

    async def close(self) -> None:
        if self.connection is not None:
            await self._pool.release(self.connection)

    async def __aenter__(self) -> 'Database':
        await self.connect()
        return self

    async def __aexit__(self,
                        type: Optional[Type[BaseException]],
                        value: Optional[BaseException],
                        traceback: 'Optional[TracebackType]') -> None:
        await self.close()

    @property
    def isSqlite(self) -> bool:
        return 'sqlite' in self._driver

    @property
    def isPostgres(self) -> bool:
        return 'psql' in self._driver

    async def cursor(self) -> aioodbc.cursor.Cursor:
        return await self.connection.cursor()

    async def commit(self) -> None:
        await self.connection.commit()
