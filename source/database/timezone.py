import aioodbc.cursor  # noqa: F401, E501

from typing import AsyncIterator, List, Tuple, cast

from ._base import Database


class DatabaseTimeZone(Database):
    async def timezone_names(self) -> AsyncIterator[Tuple[str, int]]:
        '''
        For the abbreviation conflicts of: CST, CDT, AMT, AST, GST, IST,
        KST, BST
        I have choosen: America/Chicago, America/Boa_Vista,
        America/Puerto_Rico, Asia/Muscat, Asia/Jerusalem, Asia/Seoul,
        Europe/London
        '''
        query: str = '''
SELECT abbreviation, CAST(ROUND(AVG(gmt_offset) / 60 / 15) * 60 * 15 AS INT)
    FROM timezone
    WHERE time_start >= 2114380800
        AND abbreviation NOT IN ('CST', 'CDT', 'AMT', 'AST', 'GST', 'IST',
                                 'KST', 'BST', 'UTC')
    GROUP BY abbreviation
UNION ALL
SELECT abbreviation, gmt_offset
    FROM timezone
    WHERE time_start=2147483647
        AND zone_id IN (382, 75, 294, 281, 190, 211, 159)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            async for row in await cursor.execute(query):
                yield row[0], row[1]

    async def zones(self) -> AsyncIterator[Tuple[str, int]]:
            query: str = '''
SELECT zone_id, zone_name FROM zone ORDER BY zone_id
'''
            cursor: aioodbc.cursor.Cursor
            async with await self.cursor() as cursor:
                async for row in await cursor.execute(query):
                    yield row[0], row[1]

    async def zone_transitions(self) -> List[Tuple[int, str, int, int]]:
        query: str = '''
SELECT zone_id, abbreviation, time_start, gmt_offset
    FROM timezone
    WHERE abbreviation != 'UTC'
    ORDER BY zone_id, time_start
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query)
            return [cast(Tuple[int, str, int, int], tuple(row))
                    for row in await cursor.fetchall()]
