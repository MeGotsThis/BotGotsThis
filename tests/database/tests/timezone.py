from lib.database import DatabaseTimeZone


class TestTimezone:
    DatabaseClass = DatabaseTimeZone

    async def setUpInsert(self):
        await self.execute(['''
INSERT INTO zone VALUES ('399','US','America/Los_Angeles')
''', '''
INSERT INTO timezone VALUES ('399','PDT','923220000','-25200','1')
''', '''
INSERT INTO timezone VALUES ('399','PST','941360400','-28800','0')
''', '''
INSERT INTO timezone VALUES ('399','PDT','954669600','-25200','1')
''', '''
INSERT INTO timezone VALUES ('399','PST','972810000','-28800','0')
''', '''
INSERT INTO timezone VALUES ('399','PDT','2120119200','-25200','1')
''', '''
INSERT INTO timezone VALUES ('399','PST','2140678800','-28800','0')
'''])

    async def tearDown(self):
        await self.execute(['''DROP TABLE zone''',
                            '''DROP TABLE timezone''',
                            '''DROP TABLE country''',
                            '''DROP TABLE updated''',
                            ])
        await super().tearDown()

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
