import asyncio
import sys
import unittest

import asynctest

from asynctest.mock import CoroutineMock, Mock, patch

from ..library import reload


def send(messages):
    pass


class TestLibraryReloadReloadable(unittest.TestCase):
    def test_source(self):
        self.assertIs(reload.reloadable('lib.ircmessage'), True)

    def test_items(self):
        self.assertIs(reload.reloadable('lib.items.channel'), True)

    def test_bot(self):
        self.assertIs(reload.reloadable('bot.utils'), False)
        self.assertIs(reload.reloadable('bot.globals'), False)

    def test_reload(self):
        reloadable = reload.reloadable
        self.assertIs(reloadable('pkg.botgotsthis.library.reload'), False)

    @patch('bot.globals', autospec=True)
    def test_autoload(self, mock_globals):
        mock_globals.pkgs = ['botgotsthis']
        reloadable = reload.reloadable
        self.assertIs(reloadable('pkg.botgotsthis.autoload'), False)
        self.assertIs(reloadable('pkg.botgotsthis.autoload.test'), False)
        self.assertIs(reloadable('pkg.botgotsthis.autoloadlonger'), True)
        self.assertIs(reloadable('pkg.megotsthis.autoload'), True)
        self.assertIs(reloadable('pkg.megotsthis.autoload.test'), True)
        self.assertIs(reloadable('pkg.megotsthis.autoloadlonger'), True)


class TestLibraryReloadIsSubmodule(unittest.TestCase):
    def test(self):
        self.assertIs(reload.is_submodule('lib', 'lib'), True)
        self.assertIs(reload.is_submodule('lib.a', 'lib'), True)
        self.assertIs(reload.is_submodule('lib', 'abc'), False)
        self.assertIs(reload.is_submodule('lib', 'sourcea'), False)


class TestLibraryReloadKey(unittest.TestCase):
    @patch('bot.globals', autospec=True)
    def test(self, mock_globals):
        mock_globals.pkgs = ['megotsthis', 'botgotsthis']
        order = [
            'lib.data.message',
            'lib.data',
            'lib.database.databasenone',
            'lib.database.sqlite',
            'lib.database',
            'lib.api.twitch',
            'lib.api',
            'abc.def',
            'abc',
            'zyx',
            'lib.api_longer',
            'lib.channel_longer',
            'lib.data_longer',
            'lib.database_longer',
            'lib.irccommand_longer',
            'lib.something',
            'lib.whisper_longer',
            'pkg.mebotsthis.library',
            'pkg.mebotsthis',
            'pkg.megotsthis.library',
            'pkg.botgotsthis.library.chat',
            'pkg.botgotsthis.library',
            'pkg.botgotsthis.channel_longer',
            'pkg.botgotsthis.custom_longer',
            'pkg.botgotsthis.items_longer',
            'pkg.botgotsthis.library_longer',
            'pkg.botgotsthis.manage_longer',
            'pkg.botgotsthis.something',
            'pkg.botgotsthis.tasks_longer',
            'pkg.botgotsthis.whisper_longer',
            'pkg.botgotsthis.tasks.twitch',
            'pkg.botgotsthis.tasks',
            'pkg.botgotsthis.manage.listchats',
            'pkg.botgotsthis.manage',
            'pkg.botgotsthis.custom.params',
            'pkg.botgotsthis.custom',
            'pkg.botgotsthis.channel.owner',
            'pkg.botgotsthis.channel',
            'pkg.botgotsthis.whisper.owner',
            'pkg.botgotsthis.whisper',
            'pkg.botgotsthis.items.channel',
            'pkg.botgotsthis.items',
            'pkg.botgotsthis.ircmessage',
            'pkg.megotsthis',
            'pkg.botgotsthis',
            'pkg',
            'lib.items.channel',
            'lib.items.whisper',
            'lib.items',
            'lib.irccommand.notice',
            'lib.irccommand',
            'lib.channel',
            'lib.whisper',
            'lib.ircmessage',
            'lib',
            ]
        for first, second in zip(order, order[1:]):
            self.assertLess(reload.key(first), reload.key(second),
                            (first, second))


class TestLibraryReload(asynctest.TestCase):
    def setUp(self):
        self.send = Mock(spec=send)

    @patch('pkg.botgotsthis.library.reload.reload_config')
    @patch('pkg.botgotsthis.library.reload.reload_commands')
    async def test_full_reload(self, mock_reload_command, mock_reload_config):
        self.assertIs(await reload.full_reload(self.send), True)
        self.assertEqual(self.send.call_count, 2)
        mock_reload_config.assert_called_once_with(self.send)
        mock_reload_command.assert_called_once_with(self.send)

    @patch('pkg.botgotsthis.library.reload.reload_config')
    @patch('pkg.botgotsthis.library.reload.reload_commands')
    async def test_full_reload_multiple(self, mock_reload_command,
                                        mock_reload_config):
        async def wait(*args):
            await asyncio.sleep(0.2)

        async def call_0():
            return await reload.full_reload(self.send)

        async def call_1():
            await asyncio.sleep(0.1)
            return await reload.full_reload(self.send)

        mock_reload_command.side_effect = wait
        self.assertEqual(
            await asyncio.gather(call_0(), call_1()),
            [True, True])
        self.assertEqual(self.send.call_count, 2)
        mock_reload_config.assert_called_once_with(self.send)
        mock_reload_command.assert_called_once_with(self.send)

    @patch.dict('sys.modules', autospec=True)
    @patch('importlib.reload', autospec=True)
    @patch('lib.data.timezones.load_timezones')
    async def test_reload_commands(self, mock_load_timezones, mock_reload):
        module = Mock()
        sys.modules = {'lib': module}
        self.assertIs(await reload.reload_commands(self.send), True)
        self.assertEqual(self.send.call_count, 2)
        mock_reload.assert_called_once_with(module)
        mock_load_timezones.assert_called_once_with()

    @patch.dict('sys.modules', autospec=True)
    @patch('importlib.reload', autospec=True)
    @patch('lib.data.timezones.load_timezones')
    async def test_reload_commands_multiple(self, mock_load_timezones,
                                            mock_reload):
        async def wait(*args):
            await asyncio.sleep(0.2)

        async def call_0():
            return await reload.reload_commands(self.send)

        async def call_1():
            await asyncio.sleep(0.1)
            return await reload.reload_commands(self.send)

        module = Mock()
        sys.modules = {'lib': module}
        mock_load_timezones.side_effect = wait
        self.assertEqual(
            await asyncio.gather(call_0(), call_1()),
            [True, True])
        self.assertEqual(self.send.call_count, 2)
        mock_reload.assert_called_once_with(module)
        mock_load_timezones.assert_called_once_with()

    @patch.dict('sys.modules', autospec=True)
    @patch('importlib.reload', autospec=True)
    @patch('pkg.botgotsthis.library.reload.bot')
    async def test_reload_config(self, mock_bot, mock_reload):
        module = Mock()
        originalConfig = mock_bot.config
        mock_read = CoroutineMock()
        mock_bot._config.BotConfig.return_value.read_config = mock_read
        sys.modules = {'bot._config': module}
        self.assertIs(await reload.reload_config(self.send), True)
        self.assertEqual(self.send.call_count, 2)
        self.assertEqual(mock_reload.call_count, 1)
        mock_bot._config.BotConfig.assert_called_once_with()
        mock_read.assert_called_once_with()
        self.assertNotEqual(mock_bot.config, originalConfig)

    @patch.dict('sys.modules', autospec=True)
    @patch('importlib.reload', autospec=True)
    @patch('pkg.botgotsthis.library.reload.bot')
    async def test_reload_config_multiple(self, mock_bot, mock_reload):
        async def wait(*args):
            await asyncio.sleep(0.2)

        async def call_0():
            return await reload.reload_config(self.send)

        async def call_1():
            await asyncio.sleep(0.1)
            return await reload.reload_config(self.send)

        module = Mock()
        originalConfig = mock_bot.config
        mock_read = CoroutineMock()
        mock_bot._config.BotConfig.return_value.read_config = mock_read
        sys.modules = {'bot._config': module}
        mock_read.side_effect = wait
        self.assertEqual(
            await asyncio.gather(call_0(), call_1()),
            [True, True])
        self.assertEqual(self.send.call_count, 2)
        self.assertEqual(mock_reload.call_count, 1)
        mock_bot._config.BotConfig.assert_called_once_with()
        mock_read.assert_called_once_with()
        self.assertNotEqual(mock_bot.config, originalConfig)
