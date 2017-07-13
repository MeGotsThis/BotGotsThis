import asyncio
import sys
import unittest

import asynctest

from asynctest.mock import CoroutineMock, Mock, patch

from source.public.library import reload


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
        self.assertIs(reloadable('source.public.library.reload'), False)

    def test_autoload(self):
        reloadable = reload.reloadable
        self.assertIs(reloadable('source.public.autoload'), False)
        self.assertIs(reloadable('source.public.autoload.test'), False)
        self.assertIs(reloadable('source.public.autoloadlonger'), True)
        self.assertIs(reloadable('source.private.autoload'), False)
        self.assertIs(reloadable('source.private.autoload.test'), False)
        self.assertIs(reloadable('source.private.autoloadlonger'), True)


class TestLibraryReloadIsSubmodule(unittest.TestCase):
    def test(self):
        self.assertIs(reload.is_submodule('source', 'source'), True)
        self.assertIs(reload.is_submodule('source.a', 'source'), True)
        self.assertIs(reload.is_submodule('source', 'abc'), False)
        self.assertIs(reload.is_submodule('source', 'sourcea'), False)


class TestLibraryReloadKey(unittest.TestCase):
    def test(self):
        order = ['source.data',
                 'source.data.message',
                 'source.database',
                 'source.database.databasenone',
                 'source.database.sqlite',
                 'source.api',
                 'source.api.twitch',
                 'source.public.library',
                 'source.public.library.chat',
                 'source.private.library',
                 'source.private.library.something',
                 'source.public.tasks',
                 'source.public.tasks.twitch',
                 'source.private.tasks',
                 'source.private.tasks.something',
                 'abc',
                 'source',
                 'source.api_longer',
                 'source.channel_longer',
                 'source.data_longer',
                 'source.database_longer',
                 'source.irccommand_longer',
                 'source.private_longer',
                 'source.public_longer',
                 'source.something',
                 'source.whisper_longer',
                 'source.public',
                 'source.public.channel_longer',
                 'source.public.custom_longer',
                 'source.public.library_longer',
                 'source.public.manage_longer',
                 'source.public.something',
                 'source.public.tasks_longer',
                 'source.public.whisper_longer',
                 'source.private',
                 'source.private.channel_longer',
                 'source.private.custom_longer',
                 'source.private.library_longer',
                 'source.private.manage_longer',
                 'source.private.something',
                 'source.private.tasks_longer',
                 'source.private.whisper_longer',
                 'source.public.manage',
                 'source.public.manage.listchats',
                 'source.private.manage',
                 'source.private.manage.something',
                 'source.public.custom',
                 'source.public.custom.params',
                 'source.private.custom',
                 'source.private.custom.something',
                 'source.public.channel',
                 'source.public.channel.owner',
                 'source.private.channel',
                 'source.private.channel.something',
                 'source.public.whisper',
                 'source.public.whisper.owner',
                 'source.private.whisper',
                 'source.private.whisper.something',
                 'lists.private.channel',
                 'lists.private',
                 'lists.public.channel',
                 'lists.public',
                 'lists.channel',
                 'lists.private_longer',
                 'lists.public_longer',
                 'lists.whisper',
                 'lists',
                 'source.private.ircmessage',
                 'source.public.default.ircmessage',
                 'source.irccommand.notice',
                 'source.irccommand',
                 'source.channel',
                 'source.whisper',
                 'source.ircmessage',
                 ]
        for first, second in zip(order, order[1:]):
            self.assertLess(reload.key(first), reload.key(second),
                            (first, second))


class TestLibraryReload(asynctest.TestCase):
    def setUp(self):
        self.send = Mock(spec=send)

    @patch('source.public.library.reload.reload_config')
    @patch('source.public.library.reload.reload_commands')
    async def test_full_reload(self, mock_reload_command, mock_reload_config):
        self.assertIs(await reload.full_reload(self.send), True)
        self.assertEqual(self.send.call_count, 2)
        mock_reload_config.assert_called_once_with(self.send)
        mock_reload_command.assert_called_once_with(self.send)

    @patch('source.public.library.reload.reload_config')
    @patch('source.public.library.reload.reload_commands')
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
    @patch('source.public.library.reload.bot')
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
    @patch('source.public.library.reload.bot')
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
