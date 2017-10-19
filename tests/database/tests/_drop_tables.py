import math
from lib.database import AutoJoinChannel


class TestDropTables:
    async def tearDown(self):
        await self.execute('''DROP TABLE IF EXISTS auto_join''')
        await self.execute('''DROP TABLE IF EXISTS auto_repeat''')
        await self.execute('''DROP TABLE IF EXISTS banned_channels''')
        await self.execute('''DROP TABLE IF EXISTS banned_channels_log''')
        await self.execute('''DROP TABLE IF EXISTS bot_managers''')
        await self.execute('''DROP TABLE IF EXISTS bot_managers_log''')
        await self.execute('''DROP TABLE IF EXISTS chat_properties''')
        await self.execute(
            '''DROP TABLE IF EXISTS custom_command_properties''')
        await self.execute('''DROP TABLE IF EXISTS custom_commands''')
        await self.execute('''DROP TABLE IF EXISTS custom_commands_history''')
        await self.execute('''DROP TABLE IF EXISTS chat_features''')
        await self.execute('''DROP TABLE IF EXISTS game_abbreviations''')
        await self.execute('''DROP TABLE IF EXISTS permitted_users''')
        await self.execute('''DROP TABLE IF EXISTS permitted_users_log''')
        await super().tearDown()
