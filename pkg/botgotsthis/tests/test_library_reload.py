import asyncio
import sys
import unittest

import asynctest

from asynctest.mock import CoroutineMock, Mock, patch

from pkg.botgotsthis.library import reload


def send(messages):
    pass


class TestLibraryReloadReloadable(unittest.TestCase):
    def test_source(self):
        self.assertIs(reload.reloadable('source.ircmessage'), True)

    def test_lists(self):
        self.assertIs(reload.reloadable('lists.channel'), True)

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
        self.assertIs(reload.is_submodule('source', 'source'), True)
        self.assertIs(reload.is_submodule('source.a', 'source'), True)
        self.assertIs(reload.is_submodule('source', 'abc'), False)
        self.assertIs(reload.is_submodule('source', 'sourcea'), False)


class TestLibraryReloadKey(unittest.TestCase):
    @patch('bot.globals', autospec=True)
    def test(self, mock_globals):
        mock_globals.pkgs = ['megotsthis','botgotsthis']
        order = [
            'source.data.message',
            'source.data',
            'source.database.databasenone',
            'source.database.sqlite',
            'source.database',
            'source.api.twitch',
            'source.api',
            'abc.def',
            'abc',
            'zyx',
            'source.api_longer',
            'source.channel_longer',
            'source.data_longer',
            'source.database_longer',
            'source.irccommand_longer',
            'source.something',
            'source.whisper_longer',
            'pkg.mebotsthis.library',
            'pkg.mebotsthis',
            'pkg.botgotsthis.channel_longer',
            'pkg.botgotsthis.custom_longer',
            'pkg.botgotsthis.items_longer',
            'pkg.botgotsthis.library_longer',
            'pkg.botgotsthis.manage_longer',
            'pkg.botgotsthis.something',
            'pkg.botgotsthis.tasks_longer',
            'pkg.botgotsthis.whisper_longer',
            'pkg.megotsthis.library',
            'pkg.botgotsthis.library.chat',
            'pkg.botgotsthis.library',
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
            'lists.channel',
            'lists.whisper',
            'lists',
            'source.irccommand.notice',
            'source.irccommand',
            'source.channel',
            'source.whisper',
            'source.ircmessage',
            'source',
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
    @patch('source.data.timezones.load_timezones')
    async def test_reload_commands(self, mock_load_timezones, mock_reload):
        module = Mock()
        sys.modules = {'source': module}
        self.assertIs(await reload.reload_commands(self.send), True)
        self.assertEqual(self.send.call_count, 2)
        mock_reload.assert_called_once_with(module)
        mock_load_timezones.assert_called_once_with()

    @patch.dict('sys.modules', autospec=True)
    @patch('importlib.reload', autospec=True)
    @patch('source.data.timezones.load_timezones')
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
        sys.modules = {'source': module}
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
