from tests.database.sqlite.test_database import TestSqlite
from source.database import DatabaseTimeZone


class TestSqliteTimeout(TestSqlite):
    async def setUp(self):
        await super().setUp()
        await self.cursor.close()
        await self.database.close()
        self.database = DatabaseTimeZone(self.connectionString)
        await self.database.connect()
        self.cursor = await self.database.cursor()
        await self.execute(['''
CREATE TABLE "zone" (
    "zone_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "country_code" CHAR(2) NOT NULL,
    "zone_name" VARCHAR(35) NOT NULL
)
''', '''
CREATE TABLE "timezone" (
    "zone_id" INTEGER NOT NULL,
    "abbreviation" VARCHAR(6) NOT NULL,
    "time_start" INT NOT NULL,
    "gmt_offset" INT NOT NULL,
    "dst" CHAR(1) NOT NULL
)''', '''
CREATE INDEX "idx_zone_id" ON "timezone" ("zone_id")
''', '''
CREATE INDEX "idx_time_start" ON "timezone" ("time_start")
''', '''
INSERT INTO "zone" VALUES ("399","US","America/Los_Angeles")
''', '''
INSERT INTO "timezone" VALUES ("399","PDT","923220000","-25200","1")
''', '''
INSERT INTO "timezone" VALUES ("399","PST","941360400","-28800","0")
''', '''
INSERT INTO "timezone" VALUES ("399","PDT","954669600","-25200","1")
''', '''
INSERT INTO "timezone" VALUES ("399","PST","972810000","-28800","0")
''', '''
INSERT INTO "timezone" VALUES ("399","PDT","2120119200","-25200","1")
''','''
INSERT INTO "timezone" VALUES ("399","PST","2140678800","-28800","0")
'''])

    async def test_timezone_names(self):
        self.assertCountEqual(
            [row async for row in self.database.timezone_names()],
            [('PDT', -25200), ('PST', -28800)])

    async def test_zones(self):
        self.assertCountEqual(
            [row async for row in self.database.zones()],
            [(399, 'America/Los_Angeles')])

    async def test_transitions(self):
        self.assertCountEqual(
            await self.database.zone_transitions(),
            [(399, 'PDT', 923220000, -25200),
             (399, 'PST', 941360400, -28800),
             (399, 'PDT', 954669600, -25200),
             (399, 'PST', 972810000, -28800),
             (399, 'PDT', 2120119200, -25200),
             (399, 'PST', 2140678800, -28800)])
