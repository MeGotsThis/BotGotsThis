from asynctest.mock import patch

from source.data.message import Message
from source.public.channel import mod
from tests.unittest.base_channel import TestChannel
from tests.unittest.mock_class import StrContains


class TestChannelMod(TestChannel):
    @patch('source.api.oauth.token', autospec=True)
    @patch('source.api.twitch.update', autospec=True)
    def test_status_false(self, mock_update, mock_token):
        self.assertIs(mod.commandStatus(self.args), False)
        self.permissionSet['moderator'] = True
        self.features.append('gamestatusbroadcaster')
        self.assertIs(mod.commandStatus(self.args), False)
        self.assertFalse(mock_token.called)
        self.assertFalse(mock_update.called)
        self.permissionSet['moderator'] = True
        mock_token.return_value = None
        self.features.clear()
        self.assertIs(mod.commandStatus(self.args), False)
        mock_token.assert_called_once_with('botgotsthis',
                                           database=self.database)
        self.assertFalse(mock_update.called)
        self.assertFalse(self.channel.send.called)

    @patch('source.api.oauth.token', autospec=True)
    @patch('source.api.twitch.update', autospec=True)
    def test_status(self, mock_update, mock_token):
        self.permissionSet['broadcaster'] = True
        mock_token.return_value = 'oauth:'
        message = Message('!status Kappa')
        self.assertIs(mod.commandStatus(self.args._replace(message=message)),
                      True)
        mock_token.assert_called_once_with('botgotsthis',
                                           database=self.database)
        mock_update.assert_called_once_with('botgotsthis',
                                            status='Kappa')
        self.channel.send.assert_called_once_with(
            StrContains('Status', 'Kappa'))

    @patch('source.api.oauth.token', autospec=True)
    @patch('source.api.twitch.update', autospec=True)
    def test_status_unset(self, mock_update, mock_token):
        mock_update.return_value = True
        self.permissionSet['broadcaster'] = True
        mock_token.return_value = 'oauth:'
        message = Message('!status')
        self.assertIs(mod.commandStatus(self.args._replace(message=message)),
                      True)
        mock_token.assert_called_once_with('botgotsthis',
                                           database=self.database)
        mock_update.assert_called_once_with('botgotsthis',
                                            status='')
        self.channel.send.assert_called_once_with(
            StrContains('Status', 'unset'))

    @patch('source.api.oauth.token', autospec=True)
    @patch('source.api.twitch.update', autospec=True)
    def test_status_fail(self, mock_update, mock_token):
        mock_update.return_value = False
        self.permissionSet['broadcaster'] = True
        mock_token.return_value = 'oauth:'
        message = Message('!status')
        self.assertIs(mod.commandStatus(self.args._replace(message=message)),
                      True)
        mock_token.assert_called_once_with('botgotsthis',
                                           database=self.database)
        mock_update.assert_called_once_with('botgotsthis',
                                            status='')
        self.channel.send.assert_called_once_with(
            StrContains('Status', 'fail'))

    @patch('source.api.oauth.token', autospec=True)
    @patch('source.api.twitch.update', autospec=True)
    def test_game_false(self, mock_update, mock_token):
        self.assertIs(mod.commandGame(self.args), False)
        self.permissionSet['moderator'] = True
        self.features.append('gamestatusbroadcaster')
        self.assertIs(mod.commandGame(self.args), False)
        self.assertFalse(mock_token.called)
        self.assertFalse(mock_update.called)
        self.permissionSet['moderator'] = True
        mock_token.return_value = None
        self.features.clear()
        self.assertIs(mod.commandGame(self.args), False)
        mock_token.assert_called_once_with('botgotsthis',
                                           database=self.database)
        self.assertFalse(mock_update.called)
        self.assertFalse(self.channel.send.called)

    @patch('source.api.oauth.token', autospec=True)
    @patch('source.api.twitch.update', autospec=True)
    def test_game(self, mock_update, mock_token):
        mock_update.return_value = True
        self.permissionSet['broadcaster'] = True
        self.database.getFullGameTitle.return_value = None
        mock_token.return_value = 'oauth:'
        message = Message('!game Kappa')
        self.assertIs(mod.commandGame(self.args._replace(message=message)),
                      True)
        mock_token.assert_called_once_with('botgotsthis',
                                           database=self.database)
        mock_update.assert_called_once_with('botgotsthis',
                                            game='Kappa')
        self.channel.send.assert_called_once_with(
            StrContains('Game', 'Kappa'))

    @patch('source.api.oauth.token', autospec=True)
    @patch('source.api.twitch.update', autospec=True)
    def test_game_abbreviation(self, mock_update, mock_token):
        mock_update.return_value = True
        self.permissionSet['moderator'] = True
        self.database.getFullGameTitle.return_value = 'Creative'
        mock_token.return_value = 'oauth:'
        message = Message('!game Kappa')
        self.assertIs(mod.commandGame(self.args._replace(message=message)),
                      True)
        mock_token.assert_called_once_with('botgotsthis',
                                           database=self.database)
        mock_update.assert_called_once_with('botgotsthis',
                                            game='Creative')
        self.channel.send.assert_called_once_with(
            StrContains('Game', 'Creative'))

    @patch('source.api.oauth.token', autospec=True)
    @patch('source.api.twitch.update', autospec=True)
    def test_game_pokemon(self, mock_update, mock_token):
        mock_update.return_value = True
        self.features.append('gamestatusbroadcaster')
        self.permissionSet['broadcaster'] = True
        self.database.getFullGameTitle.return_value = None
        mock_token.return_value = 'oauth:'
        message = Message('!game Pokemon Pokepark')
        self.assertIs(mod.commandGame(self.args._replace(message=message)),
                      True)
        mock_token.assert_called_once_with('botgotsthis',
                                           database=self.database)
        mock_update.assert_called_once_with('botgotsthis',
                                            game='Pokémon Poképark')
        self.channel.send.assert_called_once_with(
            StrContains('Game', 'Pokémon Poképark'))

    @patch('source.api.oauth.token', autospec=True)
    @patch('source.api.twitch.update', autospec=True)
    def test_game_fail(self, mock_update, mock_token):
        mock_update.return_value = False
        self.features.append('gamestatusbroadcaster')
        self.permissionSet['broadcaster'] = True
        self.database.getFullGameTitle.return_value = None
        mock_token.return_value = 'oauth:'
        message = Message('!game Pokemon Pokepark')
        self.assertIs(mod.commandGame(self.args._replace(message=message)),
                      True)
        mock_token.assert_called_once_with('botgotsthis',
                                           database=self.database)
        mock_update.assert_called_once_with('botgotsthis',
                                            game='Pokémon Poképark')
        self.channel.send.assert_called_once_with(
            StrContains('Game', 'fail'))

    @patch('source.api.oauth.token', autospec=True)
    @patch('source.api.twitch.update', autospec=True)
    def test_raw_game_false(self, mock_update, mock_token):
        self.assertIs(mod.commandRawGame(self.args), False)
        self.permissionSet['moderator'] = True
        self.features.append('gamestatusbroadcaster')
        self.assertIs(mod.commandRawGame(self.args), False)
        self.assertFalse(mock_token.called)
        self.assertFalse(mock_update.called)
        self.permissionSet['moderator'] = True
        mock_token.return_value = None
        self.features.clear()
        self.assertIs(mod.commandRawGame(self.args), False)
        mock_token.assert_called_once_with('botgotsthis',
                                           database=self.database)
        self.assertFalse(mock_update.called)
        self.assertFalse(self.channel.send.called)

    @patch('source.api.oauth.token', autospec=True)
    @patch('source.api.twitch.update', autospec=True)
    def test_raw_game(self, mock_update, mock_token):
        mock_update.return_value = True
        self.permissionSet['broadcaster'] = True
        mock_token.return_value = 'oauth:'
        message = Message('!setgame Pokemon')
        self.assertIs(mod.commandRawGame(self.args._replace(message=message)),
                      True)
        mock_token.assert_called_once_with('botgotsthis',
                                           database=self.database)
        mock_update.assert_called_once_with('botgotsthis',
                                            game='Pokemon')
        self.channel.send.assert_called_once_with(
            StrContains('Game', 'Pokemon'))

    @patch('source.api.oauth.token', autospec=True)
    @patch('source.api.twitch.update', autospec=True)
    def test_raw_game_fail(self, mock_update, mock_token):
        mock_update.return_value = False
        self.permissionSet['broadcaster'] = True
        mock_token.return_value = 'oauth:'
        message = Message('!setgame Pokemon')
        self.assertIs(mod.commandRawGame(self.args._replace(message=message)),
                      True)
        mock_token.assert_called_once_with('botgotsthis',
                                           database=self.database)
        mock_update.assert_called_once_with('botgotsthis',
                                            game='Pokemon')
        self.channel.send.assert_called_once_with(
            StrContains('Game', 'fail'))

    def test_purge(self):
        self.assertIs(mod.commandPurge(self.args), False)
        self.assertFalse(self.channel.send.called)
        self.assertFalse(self.database.recordTimeout.called)
        self.permissionSet['moderator'] = True
        self.permissionSet['chatModerator'] = True
        message = Message('!purge MeGotsThis')
        self.assertIs(mod.commandPurge(self.args._replace(message=message)),
                      True)
        self.channel.send.assert_called_once_with('.timeout MeGotsThis 1 ')
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', 'botgotsthis', 'purge', None, 1,
            '!purge MeGotsThis', None)

    def test_purge_reason(self):
        self.assertIs(mod.commandPurge(self.args), False)
        self.assertFalse(self.channel.send.called)
        self.assertFalse(self.database.recordTimeout.called)
        self.permissionSet['moderator'] = True
        self.permissionSet['chatModerator'] = True
        message = Message('!purge MeGotsThis Kappa')
        self.assertIs(mod.commandPurge(self.args._replace(message=message)),
                      True)
        self.channel.send.assert_called_once_with(
            '.timeout MeGotsThis 1 Kappa')
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', 'botgotsthis', 'purge', None, 1,
            '!purge MeGotsThis Kappa', 'Kappa')

    @patch('bot.globals', autospec=True)
    @patch('source.api.oauth.token', autospec=True)
    @patch('source.api.twitch.set_channel_community')
    def test_community_false(self, mock_update, mock_token, mock_globals):
        mock_globals.twitchCommunity = {
            'speedrunning': '6e940c4a-c42f-47d2-af83-0a2c7e47c421'
            }
        mock_globals.twitchCommunityId = {
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421': 'Speedrunning'
            }
        self.assertIs(mod.commandCommunity(self.args), False)
        self.permissionSet['moderator'] = True
        self.features.append('gamestatusbroadcaster')
        self.assertIs(mod.commandCommunity(self.args), False)
        self.assertFalse(mock_token.called)
        self.assertFalse(mock_update.called)
        self.permissionSet['moderator'] = True
        mock_token.return_value = None
        self.features.clear()
        self.assertIs(mod.commandCommunity(self.args), False)
        mock_token.assert_called_once_with('botgotsthis',
                                           database=self.database)
        self.assertFalse(mock_update.called)
        self.assertFalse(self.channel.send.called)

    @patch('bot.globals', autospec=True)
    @patch('source.api.oauth.token', autospec=True)
    @patch('source.api.twitch.set_channel_community')
    def test_community(self, mock_update, mock_token, mock_globals):
        mock_globals.twitchCommunity = {
            'speedrunning': '6e940c4a-c42f-47d2-af83-0a2c7e47c421'
            }
        mock_globals.twitchCommunityId = {
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421': 'Speedrunning'
            }
        mock_update.return_value = True
        self.permissionSet['broadcaster'] = True
        mock_token.return_value = 'oauth:'
        message = Message('!community speedrunning')
        self.assertIs(
            mod.commandCommunity(self.args._replace(message=message)), True)
        mock_token.assert_called_once_with('botgotsthis',
                                           database=self.database)
        mock_update.assert_called_once_with('botgotsthis', 'speedrunning')
        self.channel.send.assert_called_once_with(
            StrContains('Community', 'Speedrunning'))

    @patch('bot.globals', autospec=True)
    @patch('source.api.oauth.token', autospec=True)
    @patch('source.api.twitch.set_channel_community')
    def test_community_unset(self, mock_update, mock_token, mock_globals):
        mock_globals.twitchCommunity = {
            'speedrunning': '6e940c4a-c42f-47d2-af83-0a2c7e47c421'
            }
        mock_globals.twitchCommunityId = {
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421': 'Speedrunning'
            }
        mock_update.return_value = True
        self.permissionSet['broadcaster'] = True
        mock_token.return_value = 'oauth:'
        message = Message('!community')
        self.assertIs(
            mod.commandCommunity(self.args._replace(message=message)), True)
        mock_token.assert_called_once_with('botgotsthis',
                                           database=self.database)
        mock_update.assert_called_once_with('botgotsthis', None)
        self.channel.send.assert_called_once_with(
            StrContains('Community', 'unset'))

    @patch('bot.globals', autospec=True)
    @patch('source.api.oauth.token', autospec=True)
    @patch('source.api.twitch.set_channel_community')
    def test_community_not_exist(self, mock_update, mock_token, mock_globals):
        mock_globals.twitchCommunity = {
            'speedrunning': '6e940c4a-c42f-47d2-af83-0a2c7e47c421'
            }
        mock_globals.twitchCommunityId = {
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421': 'Speedrunning'
            }
        mock_update.return_value = False
        self.permissionSet['broadcaster'] = True
        mock_token.return_value = 'oauth:'
        message = Message('!community Kappa')
        self.assertIs(
            mod.commandCommunity(self.args._replace(message=message)), True)
        mock_token.assert_called_once_with('botgotsthis',
                                           database=self.database)
        mock_update.assert_called_once_with('botgotsthis', 'Kappa')
        self.channel.send.assert_called_once_with(
            StrContains('Community', 'Kappa', 'not', 'exist'))

    @patch('bot.globals', autospec=True)
    @patch('source.api.oauth.token', autospec=True)
    @patch('source.api.twitch.set_channel_community')
    def test_community_fail(self, mock_update, mock_token, mock_globals):
        mock_globals.twitchCommunity = {
            'speedrunning': '6e940c4a-c42f-47d2-af83-0a2c7e47c421'
            }
        mock_globals.twitchCommunityId = {
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421': 'Speedrunning'
            }
        mock_update.return_value = None
        self.permissionSet['broadcaster'] = True
        mock_token.return_value = 'oauth:'
        message = Message('!community')
        self.assertIs(
            mod.commandCommunity(self.args._replace(message=message)), True)
        mock_token.assert_called_once_with('botgotsthis',
                                           database=self.database)
        mock_update.assert_called_once_with('botgotsthis', None)
        self.channel.send.assert_called_once_with(
            StrContains('Community', 'fail'))

    def test_permit(self):
        self.channel.channel = 'megotsthis'
        self.database.isPermittedUser.return_value = False
        self.assertIs(mod.commandPermit(self.args), False)
        self.assertFalse(self.channel.send.called)
        self.assertFalse(self.database.isPermittedUser.called)
        self.assertFalse(self.database.addPermittedUser.called)
        self.assertFalse(self.database.removePermittedUser.called)

    def test_permit_add(self):
        self.channel.channel = 'megotsthis'
        self.database.isPermittedUser.return_value = False
        self.database.addPermittedUser.return_value = True
        self.permissionSet['moderator'] = True
        message = Message('!permit MeBotsThis')
        self.assertIs(mod.commandPermit(self.args._replace(message=message)),
                      True)
        self.assertTrue(self.database.isPermittedUser.called)
        self.assertTrue(self.database.addPermittedUser.called)
        self.assertFalse(self.database.removePermittedUser.called)
        self.channel.send.assert_called_once_with(
            StrContains('botgotsthis', 'mebotsthis', 'permitted',
                        'megotsthis'))

    def test_permit_remove(self):
        self.channel.channel = 'megotsthis'
        self.database.isPermittedUser.return_value = True
        self.database.removePermittedUser.return_value = True
        self.permissionSet['moderator'] = True
        message = Message('!permit MeBotsThis')
        self.assertIs(mod.commandPermit(self.args._replace(message=message)),
                      True)
        self.assertTrue(self.database.isPermittedUser.called)
        self.assertTrue(self.database.removePermittedUser.called)
        self.assertFalse(self.database.addPermittedUser.called)
        self.channel.send.assert_called_once_with(
            StrContains('botgotsthis', 'mebotsthis', 'unpermitted',
                        'megotsthis'))
