from asynctest.mock import patch

from tests.unittest.base_channel import TestChannel
from lib.data.message import Message
from tests.unittest.mock_class import StrContains

# Needs to be imported last
from pkg.botgotsthis.channel import mod


class TestChannelMod(TestChannel):
    @patch('lib.api.oauth.token')
    @patch('lib.api.twitch.update')
    async def test_status_false(self, mock_update, mock_token):
        self.assertIs(await mod.commandStatus(self.args), False)
        self.permissionSet['moderator'] = True
        self.features.append('gamestatusbroadcaster')
        self.assertIs(await mod.commandStatus(self.args), False)
        self.assertFalse(mock_token.called)
        self.assertFalse(mock_update.called)
        self.permissionSet['moderator'] = True
        mock_token.return_value = None
        self.features.clear()
        self.assertIs(await mod.commandStatus(self.args), False)
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
        self.assertIs(await mod.commandStatus(args), True)
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
        self.assertIs(await mod.commandStatus(args), True)
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
        self.assertIs(await mod.commandStatus(args), True)
        mock_token.assert_called_once_with('botgotsthis')
        mock_update.assert_called_once_with('botgotsthis',
                                            status='')
        self.channel.send.assert_called_once_with(
            StrContains('Status', 'fail'))

    @patch('lib.api.oauth.token')
    @patch('lib.api.twitch.update')
    async def test_game_false(self, mock_update, mock_token):
        self.assertIs(await mod.commandGame(self.args), False)
        self.permissionSet['moderator'] = True
        self.features.append('gamestatusbroadcaster')
        self.assertIs(await mod.commandGame(self.args), False)
        self.assertFalse(mock_token.called)
        self.assertFalse(mock_update.called)
        self.permissionSet['broadcaster'] = True
        mock_token.return_value = None
        self.features.clear()
        self.assertIs(await mod.commandGame(self.args), False)
        mock_token.assert_called_once_with('botgotsthis')
        self.assertFalse(mock_update.called)
        self.assertFalse(self.channel.send.called)

    @patch('lib.api.oauth.token')
    @patch('lib.api.twitch.update')
    async def test_game(self, mock_update, mock_token):
        mock_update.return_value = True
        self.permissionSet['broadcaster'] = True
        self.database.getFullGameTitle.return_value = None
        mock_token.return_value = 'oauth:'
        args = self.args._replace(message=Message('!game Kappa'))
        self.assertIs(await mod.commandGame(args), True)
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
        self.database.getFullGameTitle.return_value = 'Creative'
        mock_token.return_value = 'oauth:'
        args = self.args._replace(message=Message('!game Kappa'))
        self.assertIs(await mod.commandGame(args), True)
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
        self.database.getFullGameTitle.return_value = None
        mock_token.return_value = 'oauth:'
        args = self.args._replace(message=Message('!game Pokemon Pokepark'))
        self.assertIs(await mod.commandGame(args), True)
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
        self.database.getFullGameTitle.return_value = None
        mock_token.return_value = 'oauth:'
        args = self.args._replace(message=Message('!game Pokemon Pokepark'))
        self.assertIs(await mod.commandGame(args), True)
        mock_token.assert_called_once_with('botgotsthis')
        mock_update.assert_called_once_with('botgotsthis',
                                            game='Pokémon Poképark')
        self.channel.send.assert_called_once_with(
            StrContains('Game', 'fail'))

    @patch('lib.api.oauth.token')
    @patch('lib.api.twitch.update')
    async def test_raw_game_false(self, mock_update, mock_token):
        self.assertIs(await mod.commandRawGame(self.args), False)
        self.permissionSet['moderator'] = True
        self.features.append('gamestatusbroadcaster')
        self.assertIs(await mod.commandRawGame(self.args), False)
        self.assertFalse(mock_token.called)
        self.assertFalse(mock_update.called)
        self.permissionSet['moderator'] = True
        mock_token.return_value = None
        self.features.clear()
        self.assertIs(await mod.commandRawGame(self.args), False)
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
        self.assertIs(await mod.commandRawGame(args), True)
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
        self.assertIs(await mod.commandRawGame(args), True)
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
        self.assertIs(await mod.commandCommunity(self.args), False)
        self.permissionSet['moderator'] = True
        self.features.append('gamestatusbroadcaster')
        self.assertIs(await mod.commandCommunity(self.args), False)
        self.assertFalse(mock_token.called)
        self.assertFalse(mock_update.called)
        self.permissionSet['moderator'] = True
        mock_token.return_value = None
        self.features.clear()
        self.assertIs(await mod.commandCommunity(self.args), False)
        mock_token.assert_called_once_with('botgotsthis')
        self.assertFalse(mock_update.called)
        self.assertFalse(self.channel.send.called)

    @patch('bot.globals', autospec=True)
    @patch('lib.api.oauth.token')
    @patch('lib.api.twitch.set_channel_community')
    async def test_community(self, mock_update, mock_token, mock_globals):
        mock_globals.twitchCommunity = {
            'speedrunning': '6e940c4a-c42f-47d2-af83-0a2c7e47c421'
            }
        mock_globals.twitchCommunityId = {
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421': 'Speedrunning'
            }
        mock_update.return_value = ['6e940c4a-c42f-47d2-af83-0a2c7e47c421']
        self.permissionSet['broadcaster'] = True
        mock_token.return_value = 'oauth:'
        args = self.args._replace(message=Message('!community speedrunning'))
        self.assertIs(await mod.commandCommunity(args), True)
        mock_token.assert_called_once_with('botgotsthis')
        mock_update.assert_called_once_with('botgotsthis', ['speedrunning'])
        self.channel.send.assert_called_once_with(
            StrContains('Community', 'Speedrunning'))

    @patch('bot.globals', autospec=True)
    @patch('lib.api.oauth.token')
    @patch('lib.api.twitch.set_channel_community')
    async def test_community_3(self, mock_update, mock_token, mock_globals):
        mock_globals.twitchCommunity = {
            'speedrunning': '6e940c4a-c42f-47d2-af83-0a2c7e47c421',
            'programming': None
            }
        mock_globals.twitchCommunityId = {
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421': 'Speedrunning'
            }
        mock_update.return_value = ['6e940c4a-c42f-47d2-af83-0a2c7e47c421']
        self.permissionSet['broadcaster'] = True
        mock_token.return_value = 'oauth:'
        message = Message('!community Speedrunning Programming')
        args = self.args._replace(message=message)
        self.assertIs(await mod.commandCommunity(args), True)
        mock_token.assert_called_once_with('botgotsthis')
        mock_update.assert_called_once_with(
            'botgotsthis', ['Speedrunning', 'Programming'])
        self.channel.send.assert_called_once_with(
            StrContains('Community', 'Speedrunning'))

    @patch('bot.globals', autospec=True)
    @patch('lib.api.oauth.token')
    @patch('lib.api.twitch.set_channel_community')
    async def test_community_unset(self, mock_update, mock_token,
                                   mock_globals):
        mock_globals.twitchCommunity = {
            'speedrunning': '6e940c4a-c42f-47d2-af83-0a2c7e47c421'
            }
        mock_globals.twitchCommunityId = {
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421': 'Speedrunning'
            }
        mock_update.return_value = True
        self.permissionSet['broadcaster'] = True
        mock_token.return_value = 'oauth:'
        args = self.args._replace(message=Message('!community'))
        self.assertIs(await mod.commandCommunity(args), True)
        mock_token.assert_called_once_with('botgotsthis')
        mock_update.assert_called_once_with('botgotsthis', [])
        self.channel.send.assert_called_once_with(
            StrContains('Community', 'unset'))

    @patch('bot.globals', autospec=True)
    @patch('lib.api.oauth.token')
    @patch('lib.api.twitch.set_channel_community')
    async def test_community_not_exist(self, mock_update, mock_token,
                                       mock_globals):
        mock_globals.twitchCommunity = {
            'speedrunning': '6e940c4a-c42f-47d2-af83-0a2c7e47c421'
            }
        mock_globals.twitchCommunityId = {
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421': 'Speedrunning'
            }
        mock_update.return_value = []
        self.permissionSet['broadcaster'] = True
        mock_token.return_value = 'oauth:'
        args = self.args._replace(message=Message('!community Kappa'))
        self.assertIs(await mod.commandCommunity(args), True)
        mock_token.assert_called_once_with('botgotsthis')
        mock_update.assert_called_once_with('botgotsthis', ['Kappa'])
        self.channel.send.assert_called_once_with(
            StrContains('Communities', 'not', 'exist'))

    @patch('bot.globals', autospec=True)
    @patch('lib.api.oauth.token')
    @patch('lib.api.twitch.set_channel_community')
    async def test_community_fail(self, mock_update, mock_token, mock_globals):
        mock_globals.twitchCommunity = {
            'speedrunning': '6e940c4a-c42f-47d2-af83-0a2c7e47c421'
            }
        mock_globals.twitchCommunityId = {
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421': 'Speedrunning'
            }
        mock_update.return_value = None
        self.permissionSet['broadcaster'] = True
        mock_token.return_value = 'oauth:'
        args = self.args._replace(message=Message('!community'))
        self.assertIs(await mod.commandCommunity(args), True)
        mock_token.assert_called_once_with('botgotsthis')
        mock_update.assert_called_once_with('botgotsthis', [])
        self.channel.send.assert_called_once_with(
            StrContains('Community', 'fail'))

    async def test_permit(self):
        self.channel.channel = 'megotsthis'
        self.database.isPermittedUser.return_value = False
        self.assertIs(await mod.commandPermit(self.args), False)
        self.assertFalse(self.channel.send.called)
        self.assertFalse(self.database.isPermittedUser.called)
        self.assertFalse(self.database.addPermittedUser.called)
        self.assertFalse(self.database.removePermittedUser.called)

    async def test_permit_add(self):
        self.channel.channel = 'megotsthis'
        self.database.isPermittedUser.return_value = False
        self.database.addPermittedUser.return_value = True
        self.permissionSet['moderator'] = True
        args = self.args._replace(message=Message('!permit MeBotsThis'))
        self.assertIs(await mod.commandPermit(args), True)
        self.assertTrue(self.database.isPermittedUser.called)
        self.assertTrue(self.database.addPermittedUser.called)
        self.assertFalse(self.database.removePermittedUser.called)
        self.channel.send.assert_called_once_with(
            StrContains('botgotsthis', 'mebotsthis', 'permitted',
                        'megotsthis'))

    async def test_permit_remove(self):
        self.channel.channel = 'megotsthis'
        self.database.isPermittedUser.return_value = True
        self.database.removePermittedUser.return_value = True
        self.permissionSet['moderator'] = True
        args = self.args._replace(message=Message('!permit MeBotsThis'))
        self.assertIs(await mod.commandPermit(args), True)
        self.assertTrue(self.database.isPermittedUser.called)
        self.assertTrue(self.database.removePermittedUser.called)
        self.assertFalse(self.database.addPermittedUser.called)
        self.channel.send.assert_called_once_with(
            StrContains('botgotsthis', 'mebotsthis', 'unpermitted',
                        'megotsthis'))
