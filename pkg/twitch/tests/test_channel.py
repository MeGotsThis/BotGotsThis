from datetime import timedelta

from asynctest.mock import patch

from tests.unittest.base_channel import TestChannel
from lib.data.message import Message
from tests.unittest.mock_class import StrContains

# Needs to be imported last
from .. import channel


class TestTwitchChannel(TestChannel):
    @patch('lib.api.twitch.server_time')
    async def test_uptime(self, mock_server_time):
        self.channel.isStreaming = False
        self.assertIs(await channel.commandUptime(self.args), True)
        self.assertFalse(mock_server_time.called)
        self.channel.send.assert_called_once_with(
            StrContains('botgotsthis', 'not', 'streaming'))

    @patch('lib.api.twitch.server_time')
    async def test_uptime_isstreaming(self, mock_server_time):
        self.channel.isStreaming = True
        self.channel.streamingSince = self.now
        mock_server_time.return_value = self.now
        self.assertIs(await channel.commandUptime(self.args), True)
        mock_server_time.assert_called_once_with()
        self.channel.send.assert_called_once_with(
            StrContains('Uptime', str(timedelta())))

    @patch('lib.api.twitch.server_time')
    async def test_uptime_server_error(self, mock_server_time):
        self.channel.isStreaming = True
        mock_server_time.return_value = None
        self.assertIs(await channel.commandUptime(self.args), True)
        mock_server_time.assert_called_once_with()
        self.channel.send.assert_called_once_with(
            StrContains('Failed', 'twitch.tv'))

    @patch('lib.api.oauth.token')
    @patch('lib.api.twitch.update')
    async def test_status_false(self, mock_update, mock_token):
        self.assertIs(await channel.commandStatus(self.args), False)
        self.permissionSet['moderator'] = True
        self.features.append('gamestatusbroadcaster')
        self.assertIs(await channel.commandStatus(self.args), False)
        self.assertFalse(mock_token.called)
        self.assertFalse(mock_update.called)
        self.permissionSet['moderator'] = True
        mock_token.return_value = None
        self.features.clear()
        self.assertIs(await channel.commandStatus(self.args), False)
        mock_token.assert_called_once_with('botgotsthis')
        self.assertFalse(mock_update.called)
        self.assertFalse(self.channel.send.called)

    @patch('lib.api.oauth.token')
    @patch('lib.api.twitch.update')
    async def test_status(self, mock_update, mock_token):
        self.permissionSet['broadcaster'] = True
        mock_token.return_value = 'oauth:'
        message = Message('!status Kappa')
        args = self.args._replace(message=message)
        self.assertIs(await channel.commandStatus(args), True)
        mock_token.assert_called_once_with('botgotsthis')
        mock_update.assert_called_once_with('botgotsthis',
                                            status='Kappa')
        self.channel.send.assert_called_once_with(
            StrContains('Status', 'Kappa'))

    @patch('lib.api.oauth.token')
    @patch('lib.api.twitch.update')
    async def test_status_unset(self, mock_update, mock_token):
        mock_update.return_value = True
        self.permissionSet['broadcaster'] = True
        mock_token.return_value = 'oauth:'
        args = self.args._replace(message=Message('!status'))
        self.assertIs(await channel.commandStatus(args), True)
        mock_token.assert_called_once_with('botgotsthis')
        mock_update.assert_called_once_with('botgotsthis',
                                            status='')
        self.channel.send.assert_called_once_with(
            StrContains('Status', 'unset'))

    @patch('lib.api.oauth.token')
    @patch('lib.api.twitch.update')
    async def test_status_fail(self, mock_update, mock_token):
        mock_update.return_value = False
        self.permissionSet['broadcaster'] = True
        mock_token.return_value = 'oauth:'
        args = self.args._replace(message=Message('!status'))
        self.assertIs(await channel.commandStatus(args), True)
        mock_token.assert_called_once_with('botgotsthis')
        mock_update.assert_called_once_with('botgotsthis',
                                            status='')
        self.channel.send.assert_called_once_with(
            StrContains('Status', 'fail'))

    @patch('lib.api.oauth.token')
    @patch('lib.api.twitch.update')
    async def test_game_false(self, mock_update, mock_token):
        self.assertIs(await channel.commandGame(self.args), False)
        self.permissionSet['moderator'] = True
        self.features.append('gamestatusbroadcaster')
        self.assertIs(await channel.commandGame(self.args), False)
        self.assertFalse(mock_token.called)
        self.assertFalse(mock_update.called)
        self.permissionSet['broadcaster'] = True
        mock_token.return_value = None
        self.features.clear()
        self.assertIs(await channel.commandGame(self.args), False)
        mock_token.assert_called_once_with('botgotsthis')
        self.assertFalse(mock_update.called)
        self.assertFalse(self.channel.send.called)

    @patch('lib.api.oauth.token')
    @patch('lib.api.twitch.update')
    async def test_game(self, mock_update, mock_token):
        mock_update.return_value = True
        self.permissionSet['broadcaster'] = True
        self.data.getFullGameTitle.return_value = None
        mock_token.return_value = 'oauth:'
        args = self.args._replace(message=Message('!game Kappa'))
        self.assertIs(await channel.commandGame(args), True)
        mock_token.assert_called_once_with('botgotsthis')
        mock_update.assert_called_once_with('botgotsthis',
                                            game='Kappa')
        self.channel.send.assert_called_once_with(
            StrContains('Game', 'Kappa'))

    @patch('lib.api.oauth.token')
    @patch('lib.api.twitch.update')
    async def test_game_abbreviation(self, mock_update, mock_token):
        mock_update.return_value = True
        self.permissionSet['moderator'] = True
        self.data.getFullGameTitle.return_value = 'Creative'
        mock_token.return_value = 'oauth:'
        args = self.args._replace(message=Message('!game Kappa'))
        self.assertIs(await channel.commandGame(args), True)
        mock_token.assert_called_once_with('botgotsthis')
        mock_update.assert_called_once_with('botgotsthis',
                                            game='Creative')
        self.channel.send.assert_called_once_with(
            StrContains('Game', 'Creative'))

    @patch('lib.api.oauth.token')
    @patch('lib.api.twitch.update')
    async def test_game_pokemon(self, mock_update, mock_token):
        mock_update.return_value = True
        self.features.append('gamestatusbroadcaster')
        self.permissionSet['broadcaster'] = True
        self.data.getFullGameTitle.return_value = None
        mock_token.return_value = 'oauth:'
        args = self.args._replace(message=Message('!game Pokemon Pokepark'))
        self.assertIs(await channel.commandGame(args), True)
        mock_token.assert_called_once_with('botgotsthis')
        mock_update.assert_called_once_with('botgotsthis',
                                            game='Pokémon Poképark')
        self.channel.send.assert_called_once_with(
            StrContains('Game', 'Pokémon Poképark'))

    @patch('lib.api.oauth.token')
    @patch('lib.api.twitch.update')
    async def test_game_fail(self, mock_update, mock_token):
        mock_update.return_value = False
        self.features.append('gamestatusbroadcaster')
        self.permissionSet['broadcaster'] = True
        self.data.getFullGameTitle.return_value = None
        mock_token.return_value = 'oauth:'
        args = self.args._replace(message=Message('!game Pokemon Pokepark'))
        self.assertIs(await channel.commandGame(args), True)
        mock_token.assert_called_once_with('botgotsthis')
        mock_update.assert_called_once_with('botgotsthis',
                                            game='Pokémon Poképark')
        self.channel.send.assert_called_once_with(
            StrContains('Game', 'fail'))

    @patch('lib.api.oauth.token')
    @patch('lib.api.twitch.update')
    async def test_raw_game_false(self, mock_update, mock_token):
        self.assertIs(await channel.commandRawGame(self.args), False)
        self.permissionSet['moderator'] = True
        self.features.append('gamestatusbroadcaster')
        self.assertIs(await channel.commandRawGame(self.args), False)
        self.assertFalse(mock_token.called)
        self.assertFalse(mock_update.called)
        self.permissionSet['moderator'] = True
        mock_token.return_value = None
        self.features.clear()
        self.assertIs(await channel.commandRawGame(self.args), False)
        mock_token.assert_called_once_with('botgotsthis')
        self.assertFalse(mock_update.called)
        self.assertFalse(self.channel.send.called)

    @patch('lib.api.oauth.token')
    @patch('lib.api.twitch.update')
    async def test_raw_game(self, mock_update, mock_token):
        mock_update.return_value = True
        self.permissionSet['broadcaster'] = True
        mock_token.return_value = 'oauth:'
        args = self.args._replace(message=Message('!setgame Pokemon'))
        self.assertIs(await channel.commandRawGame(args), True)
        mock_token.assert_called_once_with('botgotsthis')
        mock_update.assert_called_once_with('botgotsthis',
                                            game='Pokemon')
        self.channel.send.assert_called_once_with(
            StrContains('Game', 'Pokemon'))

    @patch('lib.api.oauth.token')
    @patch('lib.api.twitch.update')
    async def test_raw_game_fail(self, mock_update, mock_token):
        mock_update.return_value = False
        self.permissionSet['broadcaster'] = True
        mock_token.return_value = 'oauth:'
        args = self.args._replace(message=Message('!setgame Pokemon'))
        self.assertIs(await channel.commandRawGame(args), True)
        mock_token.assert_called_once_with('botgotsthis')
        mock_update.assert_called_once_with('botgotsthis',
                                            game='Pokemon')
        self.channel.send.assert_called_once_with(
            StrContains('Game', 'fail'))

    @patch('bot.globals', autospec=True)
    @patch('lib.api.oauth.token')
    @patch('lib.api.twitch.set_channel_community')
    async def test_community_false(self, mock_update, mock_token,
                                   mock_globals):
        mock_globals.twitchCommunity = {
            'speedrunning': '6e940c4a-c42f-47d2-af83-0a2c7e47c421'
            }
        mock_globals.twitchCommunityId = {
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421': 'Speedrunning'
            }
        self.assertIs(await channel.commandCommunity(self.args), False)
        self.permissionSet['moderator'] = True
        self.features.append('gamestatusbroadcaster')
        self.assertIs(await channel.commandCommunity(self.args), False)
        self.assertFalse(mock_token.called)
        self.assertFalse(mock_update.called)
        self.permissionSet['moderator'] = True
        mock_token.return_value = None
        self.features.clear()
        self.assertIs(await channel.commandCommunity(self.args), False)
        mock_token.assert_called_once_with('botgotsthis')
        self.assertFalse(mock_update.called)
        self.assertFalse(self.channel.send.called)

    @patch('lib.api.oauth.token')
    @patch('lib.api.twitch.set_channel_community')
    async def test_community(self, mock_update, mock_token):
        self.data.twitch_get_community_name.return_value = 'Speedrunning'
        mock_update.return_value = ['6e940c4a-c42f-47d2-af83-0a2c7e47c421']
        self.permissionSet['broadcaster'] = True
        mock_token.return_value = 'oauth:'
        args = self.args._replace(message=Message('!community speedrunning'))
        self.assertIs(await channel.commandCommunity(args), True)
        mock_token.assert_called_once_with('botgotsthis')
        mock_update.assert_called_once_with('botgotsthis', ['speedrunning'])
        self.channel.send.assert_called_once_with(
            StrContains('Community', 'Speedrunning'))

    @patch('lib.api.oauth.token')
    @patch('lib.api.twitch.set_channel_community')
    async def test_community_3(self, mock_update, mock_token):
        self.data.twitch_get_community_name.return_value = 'Speedrunning'
        mock_update.return_value = ['6e940c4a-c42f-47d2-af83-0a2c7e47c421']
        self.permissionSet['broadcaster'] = True
        mock_token.return_value = 'oauth:'
        message = Message('!community Speedrunning Programming')
        args = self.args._replace(message=message)
        self.assertIs(await channel.commandCommunity(args), True)
        mock_token.assert_called_once_with('botgotsthis')
        mock_update.assert_called_once_with(
            'botgotsthis', ['Speedrunning', 'Programming'])
        self.channel.send.assert_called_once_with(
            StrContains('Community', 'Speedrunning'))

    @patch('lib.api.oauth.token')
    @patch('lib.api.twitch.set_channel_community')
    async def test_community_unset(self, mock_update, mock_token):
        self.data.twitch_get_community_name.return_value = 'Speedrunning'
        mock_update.return_value = True
        self.permissionSet['broadcaster'] = True
        mock_token.return_value = 'oauth:'
        args = self.args._replace(message=Message('!community'))
        self.assertIs(await channel.commandCommunity(args), True)
        mock_token.assert_called_once_with('botgotsthis')
        mock_update.assert_called_once_with('botgotsthis', [])
        self.channel.send.assert_called_once_with(
            StrContains('Community', 'unset'))

    @patch('lib.api.oauth.token')
    @patch('lib.api.twitch.set_channel_community')
    async def test_community_not_exist(self, mock_update, mock_token):
        self.data.twitch_get_community_name.return_value = 'Speedrunning'
        mock_update.return_value = []
        self.permissionSet['broadcaster'] = True
        mock_token.return_value = 'oauth:'
        args = self.args._replace(message=Message('!community Kappa'))
        self.assertIs(await channel.commandCommunity(args), True)
        mock_token.assert_called_once_with('botgotsthis')
        mock_update.assert_called_once_with('botgotsthis', ['Kappa'])
        self.channel.send.assert_called_once_with(
            StrContains('Communities', 'not', 'exist'))

    @patch('lib.api.oauth.token')
    @patch('lib.api.twitch.set_channel_community')
    async def test_community_fail(self, mock_update, mock_token):
        self.data.twitch_get_community_name.return_value = 'Speedrunning'
        mock_update.return_value = None
        self.permissionSet['broadcaster'] = True
        mock_token.return_value = 'oauth:'
        args = self.args._replace(message=Message('!community'))
        self.assertIs(await channel.commandCommunity(args), True)
        mock_token.assert_called_once_with('botgotsthis')
        mock_update.assert_called_once_with('botgotsthis', [])
        self.channel.send.assert_called_once_with(
            StrContains('Community', 'fail'))
