import tests.unittest.asynctest_fix  # noqa: F401

import unittest
from datetime import datetime

import aiohttp
import asynctest
from asynctest.mock import MagicMock, Mock, call, patch

from lib.cache import CacheStore
from bot.data import Channel
from lib.data.message import Message
from tests.unittest.base_channel import TestChannel
from tests.unittest.mock_class import StrContains, TypeMatch

# Needs to be imported last
import yarl

from ..channel import block_url


@patch(block_url.__name__ + '.check_domain_redirect')
class TestModerationChannelBlockUrlFilterNoUrl(TestChannel):
    async def test_nomod(self, mock_check):
        self.features.append('nourlredirect')
        self.assertIs(await block_url.filterNoUrlForBots(self.args), False)
        self.assertFalse(mock_check.called)

    async def test_no_match(self, mock_check):
        self.permissionSet['chatModerator'] = True
        self.features.append('nourlredirect')
        self.assertIs(await block_url.filterNoUrlForBots(self.args), False)
        self.assertFalse(mock_check.called)

    async def test_check(self, mock_check):
        message = Message('megotsthis.com')
        self.args = self.args._replace(message=message)
        self.permissionSet['chatModerator'] = True
        self.features.append('nourlredirect')
        self.assertIs(await block_url.filterNoUrlForBots(self.args), False)
        mock_check.assert_called_once_with(self.channel, 'botgotsthis',
                                           message, self.now)

    async def test_not_bannable(self, mock_check):
        message = Message('megotsthis.com')
        self.args = self.args._replace(message=message)
        self.permissionSet['chatModerator'] = True
        self.permissionSet['bannable'] = False
        self.features.append('nourlredirect')
        self.assertIs(await block_url.filterNoUrlForBots(self.args), False)
        self.assertFalse(mock_check.called)


class TestModerationChannelBlockUrlCheckDomainRedirect(asynctest.TestCase):
    def setUp(self):
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'
        self.channel.ircChannel = '#botgotsthis'
        self.now = datetime(2000, 1, 1)

        self.data = MagicMock(spec=CacheStore)
        self.data.__aenter__.return_value = self.data
        self.data.__aexit__.return_value = False

        patcher = patch('lib.cache.get_cache')
        self.addCleanup(patcher.stop)
        self.mock_cache = patcher.start()
        self.mock_cache.return_value = self.data

        patcher = patch('bot.utils.logIrcMessage', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_log = patcher.start()

        patcher = patch('bot.utils.logException', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_except = patcher.start()

        patcher = patch(block_url.__name__ + '.compare_domains', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_compare = patcher.start()
        self.mock_compare.return_value = False

        patcher = patch(block_url.__name__ + '.handle_different_domains')
        self.addCleanup(patcher.stop)
        self.mock_handle = patcher.start()

        self.mock_response = MagicMock(spec=aiohttp.ClientResponse)
        self.mock_response.__aenter__.return_value = self.mock_response
        self.mock_response.__aexit__.return_value = False
        self.mock_response.status = 200

        self.mock_session = MagicMock(spec=aiohttp.ClientSession)
        self.mock_session.__aenter__.return_value = self.mock_session
        self.mock_session.__aexit__.return_value = False
        self.mock_session.get.return_value = self.mock_response

        patcher = patch('aiohttp.ClientSession')
        self.addCleanup(patcher.stop)
        self.mock_clientsession = patcher.start()
        self.mock_clientsession.return_value = self.mock_session

    async def test_followers(self):
        self.data.twitch_num_followers.return_value = 1
        message = Message('twitch.tv')
        await block_url.check_domain_redirect(self.channel, 'botgotsthis',
                                              message, self.now)
        self.data.twitch_num_followers.assert_called_once_with('botgotsthis')
        self.assertFalse(self.mock_log.called)
        self.assertFalse(self.mock_except.called)
        self.assertFalse(self.mock_clientsession.called)
        self.assertFalse(self.mock_session.get.called)
        self.assertFalse(self.mock_compare.called)
        self.assertFalse(self.mock_handle.called)

    async def test(self):
        self.data.twitch_num_followers.return_value = 0
        self.mock_compare.return_value = True
        message = Message('twitch.tv')
        self.mock_response.url = yarl.URL('http://megotsthis.com')
        await block_url.check_domain_redirect(self.channel, 'megotsthis',
                                              message, self.now)
        self.data.twitch_num_followers.assert_called_once_with('megotsthis')
        self.mock_log.assert_called_once_with(
            StrContains('botgotsthis', 'blockurl'),
            StrContains('megotsthis', str(message)), self.now)
        self.assertTrue(self.mock_clientsession.called)
        self.mock_session.get.assert_called_once_with(
            'http://twitch.tv', headers=TypeMatch(dict))
        self.mock_compare.assert_called_once_with(
            'http://twitch.tv', 'http://megotsthis.com',
            chat=self.channel, nick='megotsthis', timestamp=self.now)
        self.mock_handle.assert_called_once_with(
            self.channel, 'megotsthis', message)
        self.assertFalse(self.mock_except.called)

    async def test_same_domain(self):
        self.data.twitch_num_followers.return_value = 0
        message = Message('twitch.tv')
        self.mock_response.url = yarl.URL('http://twitch.tv')
        await block_url.check_domain_redirect(self.channel, 'megotsthis',
                                              message, self.now)
        self.data.twitch_num_followers.assert_called_once_with('megotsthis')
        self.mock_log.assert_called_once_with(
            StrContains('botgotsthis', 'blockurl'),
            StrContains('megotsthis', str(message)), self.now)
        self.assertTrue(self.mock_clientsession.called)
        self.mock_session.get.assert_called_once_with(
            'http://twitch.tv', headers=TypeMatch(dict))
        self.mock_compare.assert_called_once_with(
            'http://twitch.tv', 'http://twitch.tv',
            chat=self.channel, nick='megotsthis', timestamp=self.now)
        self.assertFalse(self.mock_handle.called)
        self.assertFalse(self.mock_except.called)

    async def test_no_dns(self):
        self.data.twitch_num_followers.return_value = 0
        message = Message('twitch.tv')
        self.mock_session.get.side_effect = aiohttp.ClientConnectorError
        await block_url.check_domain_redirect(self.channel, 'megotsthis',
                                              message, self.now)
        self.data.twitch_num_followers.assert_called_once_with('megotsthis')
        self.mock_log.assert_called_once_with(
            StrContains('botgotsthis', 'blockurl'),
            StrContains('megotsthis', str(message)), self.now)
        self.assertTrue(self.mock_clientsession.called)
        self.mock_session.get.assert_called_once_with(
            'http://twitch.tv', headers=TypeMatch(dict))
        self.assertFalse(self.mock_handle.called)
        self.assertFalse(self.mock_compare.called)
        self.assertFalse(self.mock_except.called)

    async def test_exception(self):
        self.data.twitch_num_followers.return_value = 0
        message = Message('twitch.tv')
        self.mock_session.get.side_effect = Exception
        await block_url.check_domain_redirect(self.channel, 'megotsthis',
                                              message, self.now)
        self.data.twitch_num_followers.assert_called_once_with('megotsthis')
        self.mock_log.assert_called_once_with(
            StrContains('botgotsthis', 'blockurl'),
            StrContains('megotsthis', str(message)), self.now)
        self.assertTrue(self.mock_clientsession.called)
        self.mock_session.get.assert_called_once_with(
            'http://twitch.tv', headers=TypeMatch(dict))
        self.assertFalse(self.mock_handle.called)
        self.assertFalse(self.mock_compare.called)
        self.mock_except.assert_called_once_with(StrContains(str(message)),
                                                 TypeMatch(datetime))

    async def test_multiple(self):
        self.data.twitch_num_followers.return_value = 0
        message = Message('https://twitch.tv megotsthis.com')
        self.mock_response.url = yarl.URL('http://twitch.tv')
        await block_url.check_domain_redirect(self.channel, 'megotsthis',
                                              message, self.now)
        self.data.twitch_num_followers.assert_called_once_with('megotsthis')
        self.mock_log.assert_called_once_with(
            StrContains('botgotsthis', 'blockurl'),
            StrContains('megotsthis', str(message)), self.now)
        self.assertEqual(self.mock_clientsession.call_count, 1)
        self.assertEqual(self.mock_session.get.call_count, 2)
        self.mock_compare.assert_has_calls([
            call('https://twitch.tv', 'http://twitch.tv',
                 chat=self.channel, nick='megotsthis', timestamp=self.now),
            call('http://megotsthis.com', 'http://twitch.tv',
                 chat=self.channel, nick='megotsthis', timestamp=self.now),
            ])
        self.assertFalse(self.mock_handle.called)
        self.assertFalse(self.mock_except.called)

    async def test_multiple_first_match(self):
        self.data.twitch_num_followers.return_value = 0
        self.mock_compare.side_effect = [True, False]
        message = Message('https://twitch.tv megotsthis.com')
        self.mock_response.url = yarl.URL('http://twitch.tv')
        await block_url.check_domain_redirect(self.channel, 'megotsthis',
                                              message, self.now)
        self.data.twitch_num_followers.assert_called_once_with('megotsthis')
        self.mock_log.assert_called_once_with(
            StrContains('botgotsthis', 'blockurl'),
            StrContains('megotsthis', str(message)), self.now)
        self.assertEqual(self.mock_clientsession.call_count, 1)
        self.assertEqual(self.mock_session.get.call_count, 1)
        self.mock_compare.assert_called_once_with(
            'https://twitch.tv', 'http://twitch.tv',
            chat=self.channel, nick='megotsthis', timestamp=self.now)
        self.mock_handle.assert_called_once_with(
            self.channel, 'megotsthis', message)
        self.assertFalse(self.mock_except.called)

    async def test_multiple_exception(self):
        self.data.twitch_num_followers.return_value = 0
        message = Message('twitch.tv megotsthis.com twitch.tv')
        self.mock_response.url = yarl.URL('http://twitch.tv')
        self.mock_session.get.side_effect = [
            Exception, self.mock_response, Exception]
        await block_url.check_domain_redirect(self.channel, 'megotsthis',
                                              message, self.now)
        self.data.twitch_num_followers.assert_called_once_with('megotsthis')
        self.mock_log.assert_called_once_with(
            StrContains('botgotsthis', 'blockurl'),
            StrContains('megotsthis', str(message)), self.now)
        self.assertEqual(self.mock_session.get.call_count, 3)
        self.mock_compare.assert_called_once_with(
            'http://megotsthis.com', 'http://twitch.tv',
            chat=self.channel, nick='megotsthis', timestamp=self.now)
        self.mock_except.assert_has_calls(
            [call(StrContains(str(message)), TypeMatch(datetime)),
             call(StrContains(str(message)), TypeMatch(datetime))])


class TestModerationChannelBlockUrlCompareDomain(unittest.TestCase):
    def setUp(self):
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'
        self.channel.ircChannel = '#botgotsthis'
        self.message = Message('')
        self.now = datetime(2000, 1, 1)

        patcher = patch('bot.utils.logIrcMessage', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_log = patcher.start()

    def test(self):
        self.assertIs(
            block_url.compare_domains(
                'http://twitch.tv', 'http://twitch.tv',
                chat=self.channel, nick='megotsthis', timestamp=self.now),
            False)
        self.assertFalse(self.mock_log.called)

    def test_different_domain(self):
        self.assertIs(
            block_url.compare_domains(
                'http://megotsthis.com', 'http://twitch.tv',
                chat=self.channel, nick='megotsthis', timestamp=self.now),
            True)
        self.mock_log.assert_called_once_with(
            StrContains('botgotsthis', 'blockurl', 'match'),
            StrContains('megotsthis', 'megotsthis.com', 'twitch.tv'),
            TypeMatch(datetime))

    def test_different_page(self):
        self.assertIs(
            block_url.compare_domains(
                'http://twitch.tv/sda', 'http://twitch.tv/gamesdonequick',
                chat=self.channel, nick='megotsthis', timestamp=self.now),
            False)
        self.assertFalse(self.mock_log.called)

    def test_different_query(self):
        self.assertIs(
            block_url.compare_domains(
                'http://twitch.tv/megotsthis?test',
                'http://twitch.tv/megotsthis?Kappa',
                chat=self.channel, nick='megotsthis', timestamp=self.now),
            False)
        self.assertFalse(self.mock_log.called)

    def test_different_protocol(self):
        self.assertIs(
            block_url.compare_domains(
                'http://twitch.tv', 'https://twitch.tv',
                chat=self.channel, nick='megotsthis', timestamp=self.now),
            False)
        self.assertFalse(self.mock_log.called)

    def test_different_subdomain(self):
        self.assertIs(
            block_url.compare_domains(
                'http://blog.twitch.tv', 'http://twitch.tv',
                chat=self.channel, nick='megotsthis', timestamp=self.now),
            True)
        self.mock_log.assert_called_once_with(
            StrContains('botgotsthis', 'blockurl', 'match'),
            StrContains('megotsthis', 'blog.twitch.tv', 'twitch.tv'),
            TypeMatch(datetime))

    def test_different_subdomain_www(self):
        self.assertIs(
            block_url.compare_domains(
                'http://twitch.tv', 'https://www.twitch.tv',
                chat=self.channel, nick='megotsthis', timestamp=self.now),
            False)
        self.assertFalse(self.mock_log.called)


class TestModerationChannelBlockUrlHandleDifferentDomain(asynctest.TestCase):
    def setUp(self):
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'
        self.channel.ircChannel = '#botgotsthis'
        self.message = Message('')
        self.now = datetime(2000, 1, 1)

        self.data = MagicMock(spec=CacheStore)
        self.data.__aenter__.return_value = self.data
        self.data.__aexit__.return_value = False

        patcher = patch('lib.cache.get_cache')
        self.addCleanup(patcher.stop)
        self.mock_cache = patcher.start()
        self.mock_cache.return_value = self.data

        patcher = patch('lib.helper.timeout.timeout_user')
        self.addCleanup(patcher.stop)
        self.mock_timeout = patcher.start()

    async def test(self):
        await block_url.handle_different_domains(self.channel, 'megotsthis',
                                                 self.message)
        self.mock_cache.assert_called_once_with()
        self.mock_timeout.assert_called_once_with(
            self.data, self.channel, 'megotsthis', 'redirectUrl', 1, '',
            'Blocked Redirected URL')
