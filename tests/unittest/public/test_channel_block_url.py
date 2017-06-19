import socket
import unittest
import urllib.error

import asynctest

from datetime import datetime
from urllib.request import Request

from asynctest.mock import Mock, call, patch

from bot.data import Channel
from source.data.message import Message
from source.database import DatabaseMain
from tests.unittest.base_channel import TestChannel
from tests.unittest.mock_class import StrContains, TypeMatch

# Needs to be imported last
from source.public.channel import block_url


@patch('source.public.channel.block_url.check_domain_redirect')
class TestChannelBlockUrlFilterNoUrl(TestChannel):
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


class TestChannelBlockUrlCheckDomainRedirect(asynctest.TestCase):
    def setUp(self):
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'
        self.channel.ircChannel = '#botgotsthis'
        self.now = datetime(2000, 1, 1)

        patcher = patch('source.api.twitch.num_followers')
        self.addCleanup(patcher.stop)
        self.mock_followers = patcher.start()

        patcher = patch('bot.utils.logIrcMessage', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_log = patcher.start()

        patcher = patch('bot.utils.logException', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_except = patcher.start()

        patcher = patch('source.public.channel.block_url.compare_domains',
                        autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_compare = patcher.start()
        self.mock_compare.return_value = False

        patcher = patch(
            'source.public.channel.block_url.handle_different_domains',
            autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_handle = patcher.start()

    async def test_followers(self):
        self.mock_followers.return_value = 1
        message = Message('twitch.tv')
        await block_url.check_domain_redirect(self.channel, 'botgotsthis',
                                              message, self.now)
        self.mock_followers.assert_called_once_with('botgotsthis')
        self.assertFalse(self.mock_log.called)
        self.assertFalse(self.mock_except.called)
        #self.assertFalse(self.mock_request.called)
        self.assertFalse(self.mock_compare.called)
        self.assertFalse(self.mock_handle.called)

    async def fail_test(self):
        # TODO: Fix when asynctest is updated with magic mock
        self.mock_followers.return_value = 0
        self.mock_compare.return_value = True
        message = Message('twitch.tv')
        self.response.url = 'http://megotsthis.com'
        await block_url.check_domain_redirect(self.channel, 'megotsthis',
                                              message, self.now)
        self.mock_followers.assert_called_once_with('megotsthis')
        self.mock_log.assert_called_once_with(
            StrContains('botgotsthis', 'blockurl'),
            StrContains('megotsthis', str(message)), self.now)
        self.mock_request.assert_called_once_with(TypeMatch(Request))
        self.mock_compare.assert_called_once_with(
            'http://twitch.tv', 'http://megotsthis.com',
            chat=self.channel, nick='megotsthis', timestamp=self.now)
        self.mock_handle.assert_called_once_with(
            self.channel, 'megotsthis', message)
        self.assertFalse(self.mock_except.called)

    async def fail_test_same_domain(self):
        # TODO: Fix when asynctest is updated with magic mock
        self.mock_followers.return_value = 0
        message = Message('twitch.tv')
        self.response.url = 'http://twitch.tv'
        await block_url.check_domain_redirect(self.channel, 'megotsthis',
                                              message, self.now)
        self.mock_followers.assert_called_once_with('megotsthis')
        self.mock_log.assert_called_once_with(
            StrContains('botgotsthis', 'blockurl'),
            StrContains('megotsthis', str(message)), self.now)
        self.mock_request.assert_called_once_with(TypeMatch(Request))
        self.mock_compare.assert_called_once_with(
            'http://twitch.tv', 'http://twitch.tv',
            chat=self.channel, nick='megotsthis', timestamp=self.now)
        self.assertFalse(self.mock_handle.called)
        self.assertFalse(self.mock_except.called)

    async def fail_test_404_error(self):
        # TODO: Fix when asynctest is updated with magic mock
        self.mock_followers.return_value = 0
        message = Message('twitch.tv')
        self.mock_request.side_effect = urllib.error.HTTPError(
            'http://twitch.tv', 404, None, {}, 0)
        self.response.url = 'http://twitch.tv'
        await block_url.check_domain_redirect(self.channel, 'megotsthis',
                                              message, self.now)
        self.mock_followers.assert_called_once_with('megotsthis')
        self.mock_log.assert_called_once_with(
            StrContains('botgotsthis', 'blockurl'),
            StrContains('megotsthis', str(message)), self.now)
        self.mock_request.assert_called_once_with(TypeMatch(Request))
        self.mock_compare.assert_called_once_with(
            'http://twitch.tv', 'http://twitch.tv',
            chat=self.channel, nick='megotsthis', timestamp=self.now)
        self.assertFalse(self.mock_handle.called)
        self.assertFalse(self.mock_except.called)

    async def fail_test_502_error(self):
        # TODO: Fix when asynctest is updated with magic mock
        self.mock_followers.return_value = 0
        message = Message('twitch.tv')
        self.mock_request.side_effect = urllib.error.HTTPError(
            'http://twitch.tv', 502, None, {}, 0)
        self.response.url = 'http://twitch.tv'
        await block_url.check_domain_redirect(self.channel, 'megotsthis',
                                              message, self.now)
        self.mock_followers.assert_called_once_with('megotsthis')
        self.mock_log.assert_called_once_with(
            StrContains('botgotsthis', 'blockurl'),
            StrContains('megotsthis', str(message)), self.now)
        self.mock_request.assert_called_once_with(TypeMatch(Request))
        self.mock_compare.assert_called_once_with(
            'http://twitch.tv', 'http://twitch.tv',
            chat=self.channel, nick='megotsthis', timestamp=self.now)
        self.assertFalse(self.mock_handle.called)
        self.assertFalse(self.mock_except.called)

    async def fail_test_urlerror_no_dns(self):
        # TODO: Fix when asynctest is updated with magic mock
        self.mock_followers.return_value = 0
        message = Message('twitch.tv')
        self.mock_request.side_effect = urllib.error.URLError(
            OSError(socket.EAI_NONAME, 'no name'))
        await block_url.check_domain_redirect(self.channel, 'megotsthis',
                                              message, self.now)
        self.mock_followers.assert_called_once_with('megotsthis')
        self.mock_log.assert_called_once_with(
            StrContains('botgotsthis', 'blockurl'),
            StrContains('megotsthis', str(message)), self.now)
        self.mock_request.assert_called_once_with(TypeMatch(Request))
        self.assertFalse(self.mock_compare.called)
        self.assertFalse(self.mock_except.called)

    async def fail_test_urlerror_other(self):
        # TODO: Fix when asynctest is updated with magic mock
        self.mock_followers.return_value = 0
        message = Message('twitch.tv')
        self.mock_request.side_effect = urllib.error.URLError('error')
        await block_url.check_domain_redirect(self.channel, 'megotsthis',
                                              message, self.now)
        self.mock_followers.assert_called_once_with('megotsthis')
        self.mock_log.assert_called_once_with(
            StrContains('botgotsthis', 'blockurl'),
            StrContains('megotsthis', str(message)), self.now)
        self.mock_request.assert_called_once_with(TypeMatch(Request))
        self.mock_except.assert_called_once_with(StrContains(str(message)),
                                                 TypeMatch(datetime))
        self.assertFalse(self.mock_handle.called)
        self.assertFalse(self.mock_compare.called)

    async def fail_test_exception(self):
        # TODO: Fix when asynctest is updated with magic mock
        self.mock_followers.return_value = 0
        message = Message('twitch.tv')
        self.mock_request.side_effect = Exception
        await block_url.check_domain_redirect(self.channel, 'megotsthis',
                                              message, self.now)
        self.mock_followers.assert_called_once_with('megotsthis')
        self.mock_log.assert_called_once_with(
            StrContains('botgotsthis', 'blockurl'),
            StrContains('megotsthis', str(message)), self.now)
        self.mock_request.assert_called_once_with(TypeMatch(Request))
        self.mock_except.assert_called_once_with(StrContains(str(message)),
                                                 TypeMatch(datetime))
        self.assertFalse(self.mock_handle.called)
        self.assertFalse(self.mock_compare.called)

    async def fail_test_multiple(self):
        # TODO: Fix when asynctest is updated with magic mock
        self.mock_followers.return_value = 0
        message = Message('https://twitch.tv megotsthis.com')
        self.response.url = 'http://twitch.tv'
        await block_url.check_domain_redirect(self.channel, 'megotsthis',
                                              message, self.now)
        self.mock_followers.assert_called_once_with('megotsthis')
        self.mock_log.assert_called_once_with(
            StrContains('botgotsthis', 'blockurl'),
            StrContains('megotsthis', str(message)), self.now)
        self.assertEqual(self.mock_request.call_count, 2)
        self.mock_compare.assert_has_calls([
            call('https://twitch.tv', 'http://twitch.tv',
                 chat=self.channel, nick='megotsthis', timestamp=self.now),
            call('http://megotsthis.com', 'http://twitch.tv',
                 chat=self.channel, nick='megotsthis', timestamp=self.now),
            ])
        self.assertFalse(self.mock_handle.called)
        self.assertFalse(self.mock_except.called)

    async def fail_test_multiple_first_match(self):
        # TODO: Fix when asynctest is updated with magic mock
        self.mock_followers.return_value = 0
        self.mock_compare.side_effect = [True, False]
        message = Message('https://twitch.tv megotsthis.com')
        self.response.url = 'http://twitch.tv'
        await block_url.check_domain_redirect(self.channel, 'megotsthis',
                                              message, self.now)
        self.mock_followers.assert_called_once_with('megotsthis')
        self.mock_log.assert_called_once_with(
            StrContains('botgotsthis', 'blockurl'),
            StrContains('megotsthis', str(message)), self.now)
        self.mock_request.assert_called_once_with(TypeMatch(Request))
        self.mock_compare.assert_called_once_with(
            'https://twitch.tv', 'http://twitch.tv',
            chat=self.channel, nick='megotsthis', timestamp=self.now)
        self.mock_handle.assert_called_once_with(
            self.channel, 'megotsthis', message)
        self.assertFalse(self.mock_except.called)

    async def fail_test_multiple_exception(self):
        # TODO: Fix when asynctest is updated with magic mock
        self.mock_followers.return_value = 0
        message = Message('twitch.tv megotsthis.com twitch.tv')
        self.response.url = 'http://twitch.tv'
        self.mock_request.return_value.__enter__.side_effect = [
            Exception, self.response, Exception]
        await block_url.check_domain_redirect(self.channel, 'megotsthis',
                                              message, self.now)
        self.mock_followers.assert_called_once_with('megotsthis')
        self.mock_log.assert_called_once_with(
            StrContains('botgotsthis', 'blockurl'),
            StrContains('megotsthis', str(message)), self.now)
        self.assertEqual(self.mock_request.call_count, 3)
        self.mock_compare.assert_called_once_with(
            'http://megotsthis.com', 'http://twitch.tv',
            chat=self.channel, nick='megotsthis', timestamp=self.now)
        self.mock_except.assert_has_calls(
            [call(StrContains(str(message)), TypeMatch(datetime)),
             call(StrContains(str(message)), TypeMatch(datetime))])


class TestChannelBlockUrlCompareDomain(unittest.TestCase):
    def setUp(self):
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'
        self.channel.ircChannel = '#botgotsthis'
        self.database = Mock(spec=DatabaseMain)
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


class TestChannelBlockUrlHandleDifferentDomain(unittest.TestCase):
    def setUp(self):
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'
        self.channel.ircChannel = '#botgotsthis'
        self.database = Mock(spec=DatabaseMain)
        self.message = Message('')
        self.now = datetime(2000, 1, 1)

        patcher = patch('source.database.get_database', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_database = patcher.start()
        self.mock_database.return_value.__enter__.return_value = self.database

        patcher = patch('source.public.library.timeout.timeout_user',
                        autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_timeout = patcher.start()

    def fail_test(self):
        # TODO: Fix when asynctest is updated with magic mock
        block_url.handle_different_domains(self.channel, 'megotsthis',
                                           self.message)
        self.mock_database.assert_called_once_with()
        self.mock_timeout.assert_called_once_with(
            self.database, self.channel, 'megotsthis', 'redirectUrl', 1, '',
            'Blocked Redirected URL')
