from tests.database.sqlite.test_database import TestSqlite
from tests.database.tests.test_features import TestFeatures


class TestSqliteFeatures(TestFeatures, TestSqlite):
    async def setUp(self):
        await super().setUp()
        await self.execute('''
CREATE TABLE chat_features (
    broadcaster VARCHAR NOT NULL,
    feature VARCHAR NOT NULL,
    PRIMARY KEY (broadcaster, feature)
)''')
