from tests.database.postgres.test_database import TestPostgres
from tests.database.tests.test_chat_properties import TestChatProperties


class TestPostgresChatProperties(TestChatProperties, TestPostgres):
    async def setUp(self):
        await super().setUp()
        await self.execute('''
CREATE TABLE chat_properties (
    broadcaster VARCHAR NOT NULL,
    property VARCHAR NOT NULL,
    value VARCHAR NOT NULL,
    PRIMARY KEY (broadcaster, property)
)''')
