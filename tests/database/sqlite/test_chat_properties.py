from tests.database.sqlite.test_database import TestSqlite
from tests.database.tests.test_chat_properties import TestChatProperties


class TestSqliteChatProperties(TestChatProperties, TestSqlite):
    async def setUp(self):
        await super().setUp()
        await self.execute('''
CREATE TABLE chat_properties (
    broadcaster VARCHAR NOT NULL,
    property VARCHAR NOT NULL,
    value VARCHAR NOT NULL,
    PRIMARY KEY (broadcaster, property)
)''')
