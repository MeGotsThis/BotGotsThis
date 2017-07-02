from tests.database.postgres.test_database import TestPostgres
from tests.database.tests.features import TestFeatures


class TestPostgresFeatures(TestFeatures, TestPostgres):
    async def setUp(self):
        await super().setUp()
        await self.execute('''
CREATE TABLE chat_features (
    broadcaster VARCHAR NOT NULL,
    feature VARCHAR NOT NULL,
    PRIMARY KEY (broadcaster, feature)
)''')
