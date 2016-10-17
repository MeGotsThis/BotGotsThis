import unittest
from bot.data import Channel
from bot.twitchmessage import IrcMessageTags
from source.data import permissions
from unittest.mock import Mock, patch


class TestDataChatPermissions(unittest.TestCase):
    def setUp(self):
        self.tags = IrcMessageTags()
        self.tags['badges'] = ''
        self.tags['color'] = ''
        self.tags['display-name'] = 'BotGotsThis'
        self.tags['mod'] = '0'
        self.tags['room-id'] = '1'
        self.tags['subscriber'] = '0'
        self.tags['user-id'] = '1'
        self.tags['user-type'] = ''
        self.user = 'botgotsthis'
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'mebotsthis'
        self.channel.isMod = False

        patcher = patch('bot.config')
        self.addCleanup(patcher.stop)
        self.mock_config = patcher.start()
        self.mock_config.botnick = 'botgotsthis'
        self.mock_config.owner = 'megotsthis'

    def test_readonly(self):
        perm = permissions.ChatPermissionSet(self.tags, self.user,
                                             self.channel, False)
        with self.assertRaises(AttributeError):
            perm.owner = True
        with self.assertRaises(AttributeError):
            perm.twitchStaff = True
        with self.assertRaises(AttributeError):
            perm.twitchAdmin = True
        with self.assertRaises(AttributeError):
            perm.globalModerator = True
        with self.assertRaises(AttributeError):
            perm.broadcaster = True
        with self.assertRaises(AttributeError):
            perm.moderator = True
        with self.assertRaises(AttributeError):
            perm.subscriber = True
        with self.assertRaises(AttributeError):
            perm.bannable = True
        with self.assertRaises(AttributeError):
            perm.permitted = True
        with self.assertRaises(AttributeError):
            perm.inOwnerChannel = True
        with self.assertRaises(AttributeError):
            perm.chatModerator = True

    def test_owner(self):
        self.user = 'megotsthis'
        perm = permissions.ChatPermissionSet(self.tags, self.user,
                                             self.channel, False)
        self.assertIs(perm.owner, True)
        self.assertIs(perm.twitchStaff, True)
        self.assertIs(perm.twitchAdmin, True)
        self.assertIs(perm.globalModerator, True)
        self.assertIs(perm.broadcaster, True)
        self.assertIs(perm.moderator, True)
        self.assertIs(perm.subscriber, True)
        self.assertIs(perm.permitted, False)
        self.assertIs(perm.bannable, True)

    def test_staff(self):
        self.tags['user-type'] = 'staff'
        perm = permissions.ChatPermissionSet(self.tags, self.user,
                                             self.channel, False)
        self.assertIs(perm.owner, False)
        self.assertIs(perm.twitchStaff, True)
        self.assertIs(perm.twitchAdmin, True)
        self.assertIs(perm.globalModerator, True)
        self.assertIs(perm.broadcaster, True)
        self.assertIs(perm.moderator, True)
        self.assertIs(perm.subscriber, True)
        self.assertIs(perm.permitted, True)
        self.assertIs(perm.bannable, False)

    def test_admin(self):
        self.tags['user-type'] = 'admin'
        perm = permissions.ChatPermissionSet(self.tags, self.user,
                                             self.channel, False)
        self.assertIs(perm.owner, False)
        self.assertIs(perm.twitchStaff, False)
        self.assertIs(perm.twitchAdmin, True)
        self.assertIs(perm.globalModerator, True)
        self.assertIs(perm.broadcaster, True)
        self.assertIs(perm.moderator, True)
        self.assertIs(perm.subscriber, True)
        self.assertIs(perm.permitted, True)
        self.assertIs(perm.bannable, False)

    def test_global_mod(self):
        self.tags['user-type'] = 'global_mod'
        perm = permissions.ChatPermissionSet(self.tags, self.user,
                                             self.channel, False)
        self.assertIs(perm.owner, False)
        self.assertIs(perm.twitchStaff, False)
        self.assertIs(perm.twitchAdmin, False)
        self.assertIs(perm.globalModerator, True)
        self.assertIs(perm.broadcaster, True)
        self.assertIs(perm.moderator, True)
        self.assertIs(perm.subscriber, True)
        self.assertIs(perm.permitted, True)
        self.assertIs(perm.bannable, False)

    def test_broadcaster(self):
        self.user = 'mebotsthis'
        perm = permissions.ChatPermissionSet(self.tags, self.user,
                                             self.channel, False)
        self.assertIs(perm.owner, False)
        self.assertIs(perm.twitchStaff, False)
        self.assertIs(perm.twitchAdmin, False)
        self.assertIs(perm.globalModerator, False)
        self.assertIs(perm.broadcaster, True)
        self.assertIs(perm.moderator, True)
        self.assertIs(perm.subscriber, True)
        self.assertIs(perm.permitted, True)
        self.assertIs(perm.bannable, False)

    def test_moderator(self):
        self.tags['user-type'] = 'mod'
        self.tags['mod'] = '1'
        perm = permissions.ChatPermissionSet(self.tags, self.user,
                                             self.channel, False)
        self.assertIs(perm.owner, False)
        self.assertIs(perm.twitchStaff, False)
        self.assertIs(perm.twitchAdmin, False)
        self.assertIs(perm.globalModerator, False)
        self.assertIs(perm.broadcaster, False)
        self.assertIs(perm.moderator, True)
        self.assertIs(perm.subscriber, False)
        self.assertIs(perm.permitted, True)
        self.assertIs(perm.bannable, False)

    def test_subscriber(self):
        self.tags['subscriber'] = '1'
        perm = permissions.ChatPermissionSet(self.tags, self.user,
                                             self.channel, False)
        self.assertIs(perm.owner, False)
        self.assertIs(perm.twitchStaff, False)
        self.assertIs(perm.twitchAdmin, False)
        self.assertIs(perm.globalModerator, False)
        self.assertIs(perm.broadcaster, False)
        self.assertIs(perm.moderator, False)
        self.assertIs(perm.subscriber, True)
        self.assertIs(perm.permitted, False)
        self.assertIs(perm.bannable, True)

    def test_permittable(self):
        perm = permissions.ChatPermissionSet(self.tags, self.user,
                                             self.channel, True)
        self.assertIs(perm.owner, False)
        self.assertIs(perm.twitchStaff, False)
        self.assertIs(perm.twitchAdmin, False)
        self.assertIs(perm.globalModerator, False)
        self.assertIs(perm.broadcaster, False)
        self.assertIs(perm.moderator, False)
        self.assertIs(perm.subscriber, False)
        self.assertIs(perm.permitted, True)
        self.assertIs(perm.bannable, True)

    def test_bannable_true(self):
        perm = permissions.ChatPermissionSet(self.tags, self.user,
                                             self.channel, False)
        self.assertIs(perm.owner, False)
        self.assertIs(perm.twitchStaff, False)
        self.assertIs(perm.twitchAdmin, False)
        self.assertIs(perm.globalModerator, False)
        self.assertIs(perm.broadcaster, False)
        self.assertIs(perm.moderator, False)
        self.assertIs(perm.subscriber, False)
        self.assertIs(perm.permitted, False)
        self.assertIs(perm.bannable, True)

    def test_bannable_true_owner(self):
        self.user = 'megotsthis'
        perm = permissions.ChatPermissionSet(self.tags, self.user,
                                             self.channel, False)
        self.assertIs(perm.owner, True)
        self.assertIs(perm.twitchStaff, True)
        self.assertIs(perm.twitchAdmin, True)
        self.assertIs(perm.globalModerator, True)
        self.assertIs(perm.broadcaster, True)
        self.assertIs(perm.moderator, True)
        self.assertIs(perm.subscriber, True)
        self.assertIs(perm.permitted, False)
        self.assertIs(perm.bannable, True)

    def test_bannable_false_broadcaster(self):
        self.user = 'mebotsthis'
        perm = permissions.ChatPermissionSet(self.tags, self.user,
                                             self.channel, False)
        self.assertIs(perm.owner, False)
        self.assertIs(perm.twitchStaff, False)
        self.assertIs(perm.twitchAdmin, False)
        self.assertIs(perm.globalModerator, False)
        self.assertIs(perm.broadcaster, True)
        self.assertIs(perm.moderator, True)
        self.assertIs(perm.subscriber, True)
        self.assertIs(perm.permitted, True)
        self.assertIs(perm.bannable, False)

    def test_bannable_false_owner_broadcaster(self):
        self.user = 'megotsthis'
        self.channel.channel = 'megotsthis'
        perm = permissions.ChatPermissionSet(self.tags, self.user,
                                             self.channel, False)
        self.assertIs(perm.owner, True)
        self.assertIs(perm.twitchStaff, True)
        self.assertIs(perm.twitchAdmin, True)
        self.assertIs(perm.globalModerator, True)
        self.assertIs(perm.broadcaster, True)
        self.assertIs(perm.moderator, True)
        self.assertIs(perm.subscriber, True)
        self.assertIs(perm.permitted, True)
        self.assertIs(perm.bannable, False)

    def test_bannable_false_moderator(self):
        self.tags['user-type'] = 'mod'
        self.tags['mod'] = '1'
        perm = permissions.ChatPermissionSet(self.tags, self.user,
                                             self.channel, False)
        self.assertIs(perm.owner, False)
        self.assertIs(perm.twitchStaff, False)
        self.assertIs(perm.twitchAdmin, False)
        self.assertIs(perm.globalModerator, False)
        self.assertIs(perm.broadcaster, False)
        self.assertIs(perm.moderator, True)
        self.assertIs(perm.subscriber, False)
        self.assertIs(perm.permitted, True)
        self.assertIs(perm.bannable, False)

    def test_no_permission(self):
        perm = permissions.ChatPermissionSet(self.tags, self.user,
                                             self.channel, False)
        self.assertIs(perm.owner, False)
        self.assertIs(perm.twitchStaff, False)
        self.assertIs(perm.twitchAdmin, False)
        self.assertIs(perm.globalModerator, False)
        self.assertIs(perm.broadcaster, False)
        self.assertIs(perm.moderator, False)
        self.assertIs(perm.subscriber, False)
        self.assertIs(perm.bannable, True)

    def test_not_in_owner_channel(self):
        perm = permissions.ChatPermissionSet(self.tags, self.user,
                                             self.channel, False)
        self.assertIs(perm.inOwnerChannel, False)

    def test_in_owner_channel_owner(self):
        self.channel.channel = 'megotsthis'
        perm = permissions.ChatPermissionSet(self.tags, self.user,
                                             self.channel, False)
        self.assertIs(perm.inOwnerChannel, True)

    def test_in_owner_channel_bot(self):
        self.channel.channel = 'botgotsthis'
        perm = permissions.ChatPermissionSet(self.tags, self.user,
                                             self.channel, False)
        self.assertIs(perm.inOwnerChannel, True)

    def test_chatModerator(self):
        perm = permissions.ChatPermissionSet(self.tags, self.user,
                                             self.channel, False)
        self.assertIs(perm.chatModerator, False)

    def test_not_chatModerator(self):
        self.channel.isMod = True
        perm = permissions.ChatPermissionSet(self.tags, self.user,
                                             self.channel, False)
        self.assertIs(perm.chatModerator, True)

    def test_getitem_except(self):
        perm = permissions.ChatPermissionSet(self.tags, self.user,
                                             self.channel, False)
        with self.assertRaises(KeyError):
            perm['Kappa']
        with self.assertRaises(TypeError):
            perm['owner'] = True

    def test_getitem_true(self):
        self.user = 'megotsthis'
        self.channel.channel = 'megotsthis'
        self.channel.isMod = True
        perm = permissions.ChatPermissionSet(self.tags, self.user,
                                             self.channel, True)
        self.assertIs(perm['owner'], True)
        self.assertIs(perm['twitchStaff'], True)
        self.assertIs(perm['staff'], True)
        self.assertIs(perm['twitchAdmin'], True)
        self.assertIs(perm['admin'], True)
        self.assertIs(perm['globalModerator'], True)
        self.assertIs(perm['globalMod'], True)
        self.assertIs(perm['broadcaster'], True)
        self.assertIs(perm['moderator'], True)
        self.assertIs(perm['subscriber'], True)
        self.assertIs(perm['permitted'], True)
        self.assertIs(perm['inOwnerChannel'], True)
        self.assertIs(perm['ownerChan'], True)
        self.assertIs(perm['chatModerator'], True)
        self.assertIs(perm['channelModerator'], True)
        self.assertIs(perm['bannable'], False)

    def test_getitem_false(self):
        perm = permissions.ChatPermissionSet(self.tags, self.user,
                                             self.channel, False)
        self.assertIs(perm['owner'], False)
        self.assertIs(perm['twitchStaff'], False)
        self.assertIs(perm['staff'], False)
        self.assertIs(perm['twitchAdmin'], False)
        self.assertIs(perm['admin'], False)
        self.assertIs(perm['globalModerator'], False)
        self.assertIs(perm['globalMod'], False)
        self.assertIs(perm['broadcaster'], False)
        self.assertIs(perm['moderator'], False)
        self.assertIs(perm['subscriber'], False)
        self.assertIs(perm['permitted'], False)
        self.assertIs(perm['inOwnerChannel'], False)
        self.assertIs(perm['ownerChan'], False)
        self.assertIs(perm['chatModerator'], False)
        self.assertIs(perm['channelModerator'], False)
        self.assertIs(perm['bannable'], True)

    def test_tags_None(self):
        perm = permissions.ChatPermissionSet(None, self.user, self.channel,
                                             False)
        self.assertIs(perm.owner, False)
        self.assertIs(perm.twitchStaff, False)
        self.assertIs(perm.twitchAdmin, False)
        self.assertIs(perm.globalModerator, False)
        self.assertIs(perm.broadcaster, False)
        self.assertIs(perm.moderator, False)
        self.assertIs(perm.subscriber, False)
        self.assertIs(perm.permitted, False)
        self.assertIs(perm.bannable, True)


class TestDataWhisperPermissions(unittest.TestCase):
    def setUp(self):
        self.tags = IrcMessageTags()
        self.tags['badges'] = ''
        self.tags['color'] = ''
        self.tags['display-name'] = 'BotGotsThis'
        self.tags['user-id'] = '1'
        self.tags['user-type'] = ''
        self.tags['message-id'] = '1'
        self.tags['thread-id'] = '1'
        self.user = 'botgotsthis'

        patcher = patch('bot.config')
        self.addCleanup(patcher.stop)
        self.mock_config = patcher.start()
        self.mock_config.owner = 'megotsthis'

    def test_readonly(self):
        perm = permissions.WhisperPermissionSet(self.tags, self.user)
        with self.assertRaises(AttributeError):
            perm.owner = True
        with self.assertRaises(AttributeError):
            perm.twitchStaff = True
        with self.assertRaises(AttributeError):
            perm.twitchAdmin = True
        with self.assertRaises(AttributeError):
            perm.globalModerator = True

    def test_owner(self):
        self.user = 'megotsthis'
        perm = permissions.WhisperPermissionSet(self.tags, self.user)
        self.assertIs(perm.owner, True)
        self.assertIs(perm.twitchStaff, True)
        self.assertIs(perm.twitchAdmin, True)
        self.assertIs(perm.globalModerator, True)

    def test_staff(self):
        self.tags['user-type'] = 'staff'
        perm = permissions.WhisperPermissionSet(self.tags, self.user)
        self.assertIs(perm.owner, False)
        self.assertIs(perm.twitchStaff, True)
        self.assertIs(perm.twitchAdmin, True)
        self.assertIs(perm.globalModerator, True)

    def test_admin(self):
        self.tags['user-type'] = 'admin'
        perm = permissions.WhisperPermissionSet(self.tags, self.user)
        self.assertIs(perm.owner, False)
        self.assertIs(perm.twitchStaff, False)
        self.assertIs(perm.twitchAdmin, True)
        self.assertIs(perm.globalModerator, True)

    def test_global_mod(self):
        self.tags['user-type'] = 'global_mod'
        perm = permissions.WhisperPermissionSet(self.tags, self.user)
        self.assertIs(perm.owner, False)
        self.assertIs(perm.twitchStaff, False)
        self.assertIs(perm.twitchAdmin, False)
        self.assertIs(perm.globalModerator, True)

    def test_no_permission(self):
        perm = permissions.WhisperPermissionSet(self.tags, self.user)
        self.assertIs(perm.owner, False)
        self.assertIs(perm.twitchStaff, False)
        self.assertIs(perm.twitchAdmin, False)
        self.assertIs(perm.globalModerator, False)

    def test_getitem_except(self):
        perm = permissions.WhisperPermissionSet(self.tags, self.user)
        with self.assertRaises(KeyError):
            perm['Kappa']
        with self.assertRaises(TypeError):
            perm['owner'] = True

    def test_getitem_true(self):
        self.user = 'megotsthis'
        perm = permissions.WhisperPermissionSet(self.tags, self.user)
        self.assertIs(perm['owner'], True)
        self.assertIs(perm['twitchStaff'], True)
        self.assertIs(perm['staff'], True)
        self.assertIs(perm['twitchAdmin'], True)
        self.assertIs(perm['admin'], True)
        self.assertIs(perm['globalModerator'], True)
        self.assertIs(perm['globalMod'], True)

    def test_getitem_false(self):
        perm = permissions.WhisperPermissionSet(self.tags, self.user)
        self.assertIs(perm['owner'], False)
        self.assertIs(perm['twitchStaff'], False)
        self.assertIs(perm['staff'], False)
        self.assertIs(perm['twitchAdmin'], False)
        self.assertIs(perm['admin'], False)
        self.assertIs(perm['globalModerator'], False)
        self.assertIs(perm['globalMod'], False)
