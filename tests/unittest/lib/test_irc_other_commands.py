import asyncio
import unittest
from datetime import datetime

import asynctest
from asynctest.mock import MagicMock, Mock, patch

from bot.data import Channel
from bot.data._error import LoginUnsuccessful
from bot.twitchmessage import IrcMessageTags
from lib.cache import CacheStore
from lib.ircmessage import clearchat, notice, userstate


class TestUserState(unittest.TestCase):
    def setUp(self):
        patcher = patch('bot.globals', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_globals = patcher.start()
        self.cache = datetime(2000, 1, 1)
        self.mock_globals.emoteset = [0]
        self.mock_globals.globalEmotesCache = self.cache
        self.tags = IrcMessageTags(IrcMessageTags.parseTags(
            'badges=broadcaster/1;color=;display-name=BotGotsThis;'
            'emote-sets=0;mod=0;subscriber=0;turbo=0;user-type='))
        self.channel = Mock(spec=Channel)
        self.channel.isMod = False
        self.channel.isSubscriber = False

        patcher = patch('lib.ircmessage.userstate.handle_emote_set')
        self.addCleanup(patcher.stop)
        self.mock_handle_emote = patcher.start()

    def test_parse(self):
        userstate.parse(self.channel, self.tags)
        self.assertEqual(self.mock_globals.displayName, 'BotGotsThis')
        self.assertIs(self.mock_globals.isTwitchStaff, False)
        self.assertIs(self.mock_globals.isTwitchAdmin, False)
        self.assertIs(self.mock_globals.isGlobalMod, False)
        self.assertIs(self.channel.isMod, False)
        self.assertIs(self.channel.isSubscriber, False)

    def test_parse_twitch_staff(self):
        self.tags['user-type'] = 'staff'
        userstate.parse(self.channel, self.tags)
        self.assertIs(self.mock_globals.isTwitchStaff, True)
        self.assertIs(self.mock_globals.isTwitchAdmin, True)
        self.assertIs(self.mock_globals.isGlobalMod, True)
        self.assertIs(self.channel.isMod, True)
        self.assertIs(self.channel.isSubscriber, False)

    def test_parse_twitch_admin(self):
        self.tags['user-type'] = 'admin'
        userstate.parse(self.channel, self.tags)
        self.assertIs(self.mock_globals.isTwitchStaff, False)
        self.assertIs(self.mock_globals.isTwitchAdmin, True)
        self.assertIs(self.mock_globals.isGlobalMod, True)
        self.assertIs(self.channel.isMod, True)
        self.assertIs(self.channel.isSubscriber, False)

    def test_parse_global_mod(self):
        self.tags['user-type'] = 'global_mod'
        userstate.parse(self.channel, self.tags)
        self.assertIs(self.mock_globals.isTwitchStaff, False)
        self.assertIs(self.mock_globals.isTwitchAdmin, False)
        self.assertIs(self.mock_globals.isGlobalMod, True)
        self.assertIs(self.channel.isMod, True)
        self.assertIs(self.channel.isSubscriber, False)

    def test_parse_moderator(self):
        self.tags['user-type'] = 'mod'
        self.tags['mod'] = '1'
        userstate.parse(self.channel, self.tags)
        self.assertIs(self.mock_globals.isTwitchStaff, False)
        self.assertIs(self.mock_globals.isTwitchAdmin, False)
        self.assertIs(self.mock_globals.isGlobalMod, False)
        self.assertIs(self.channel.isMod, True)
        self.assertIs(self.channel.isSubscriber, False)

    def test_parse_subscriber(self):
        self.tags['subscriber'] = '1'
        userstate.parse(self.channel, self.tags)
        self.assertIs(self.channel.isSubscriber, True)

    def test_parse_emote_sets(self):
        self.tags['emote-sets'] = '0'
        userstate.parse(self.channel, self.tags)
        self.mock_handle_emote.assert_called_once_with({0})

    def test_parse_emote_sets_changed(self):
        self.tags['emote-sets'] = '0,1'
        userstate.parse(self.channel, self.tags)
        self.mock_handle_emote.assert_called_once_with({0, 1})

    def test_parse_emote_sets_turbo_special(self):
        self.tags['emote-sets'] = '0,33,42'
        userstate.parse(self.channel, self.tags)
        self.mock_handle_emote.assert_called_once_with({0})

    def test_parse_emote_sets_empty(self):
        del self.tags['emote-sets']
        userstate.parse(self.channel, self.tags)
        self.assertFalse(self.mock_handle_emote.called)

    def test_parse_channel_none(self):
        self.tags['user-type'] = 'staff'
        userstate.parse(None, self.tags)
        self.assertEqual(self.mock_globals.displayName, 'BotGotsThis')
        self.assertIs(self.mock_globals.isTwitchStaff, True)
        self.assertIs(self.mock_globals.isTwitchAdmin, True)
        self.assertIs(self.mock_globals.isGlobalMod, True)
        self.assertIs(self.channel.isMod, False)
        self.assertIs(self.channel.isSubscriber, False)

    def test_parse_tags_none(self):
        userstate.parse(self.channel, None)


class TestUserStateHandleEmote(asynctest.TestCase):
    def setUp(self):
        self.data = MagicMock(spec=CacheStore)
        self.data.__aenter__.return_value = self.data
        self.data.__aexit__.return_value = False

        patcher = patch('lib.cache.get_cache')
        self.addCleanup(patcher.stop)
        self.mock_data = patcher.start()
        self.mock_data.return_value = self.data

    async def test(self):
        await userstate.handle_emote_set({0})
        self.assertTrue(self.data.twitch_load_emotes.called)

    async def test_multiple(self):
        async def wait(*args, **kwargs):
            await asyncio.sleep(0.2)
            return {0}

        async def call_0():
            await userstate.handle_emote_set({0})

        async def call_1():
            await asyncio.sleep(0.1)
            await userstate.handle_emote_set({0})

        self.data.twitch_load_emotes.side_effect = wait
        await asyncio.gather(call_0(), call_1())
        self.assertEqual(self.data.twitch_load_emotes.call_count, 1)


class TestClearChat(unittest.TestCase):
    def setUp(self):
        patcher = patch('bot.config', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_config = patcher.start()
        self.mock_config.botnick = 'botgotsthis'
        self.channel = Mock(spec=Channel)
        self.channel.isMod = True

    def test(self):
        clearchat.parse(self.channel, 'botgotsthis')
        self.assertIs(self.channel.isMod, False)
        self.channel.clear.assert_called_once_with()

    def test_channel_None(self):
        clearchat.parse(None, 'botgotsthis')
        self.assertIs(self.channel.isMod, True)
        self.assertFalse(self.channel.clear.called)

    def test_nick_None(self):
        clearchat.parse(self.channel, None)
        self.assertIs(self.channel.isMod, True)
        self.assertFalse(self.channel.clear.called)

    def test_nick_not_bot(self):
        clearchat.parse(self.channel, 'megotsthis')
        self.assertIs(self.channel.isMod, True)
        self.assertFalse(self.channel.clear.called)


class TestNotice(unittest.TestCase):
    def setUp(self):
        self.channel = Mock(spec=Channel)
        self.channel.isMod = True

    def test_invalid_login(self):
        self.assertRaises(LoginUnsuccessful, notice.parse, None, None, None,
                          'Login unsuccessful')

    def test_sending_messages_quickly(self):
        tags = IrcMessageTags(IrcMessageTags.parseTags('msg-id=msg_ratelimit'))
        notice.parse(
            tags, self.channel, None,
            'Your message was not sent because you are sending messages too '
            'quickly.')
        self.assertIs(self.channel.isMod, False)
        self.assertFalse(self.channel.clear.called)

    def test_None(self):
        notice.parse(None, None, None, None)
