import asynctest

from asynctest.mock import CoroutineMock, MagicMock, patch

import bot

config_data = '''
[TWITCH]
awsServer =
awsPort = 0

[BOT]
botnick = 
password = 
owner = 

development = 0

messageLimit = 0
modLimit = 0
modSpamLimit = 0
publicLimit = 0
publicDelay = 0
messageSpan = 0
whiperLimit = 0
whiperSpan = 0

customMessageCooldown = 0
customMessageUserCooldown = 0
customMessageUrlTimeout = 0

joinLimit = 0
joinPerSecond = 0

spamModeratorCooldown = 0

warningDuration = 0
moderatorDefaultTimeout0 = 0
moderatorDefaultTimeout1 = 0
moderatorDefaultTimeout2 = 0

httpTimeout = 0

ircLogFolder = ircLogs
exceptionLog = exception.log

[DATABASE]
main =
oauth = 
timeout = 
timezone = 

[twitch]
twitchClientID = 
twitchSecret = 
redirectUri = 
'''  # noqa: W291


class TestConfigReader(asynctest.TestCase):
    def setUp(self):
        patcher = patch('os.path.isfile')
        self.addCleanup(patcher.stop)
        self.mock_isfile = patcher.start()
        self.mock_isfile.return_value = True

        patcher = patch('os.path.isdir')
        self.addCleanup(patcher.stop)
        self.mock_isdir = patcher.start()
        self.mock_isdir.return_value = False

        patcher = patch('os.mkdir')
        self.addCleanup(patcher.stop)
        self.mock_mkdir = patcher.start()

        patcher = patch('aiofiles.open')
        self.addCleanup(patcher.stop)
        self.mock_open = patcher.start()

        self.file_mock = MagicMock()
        self.file_mock.__aenter__ = CoroutineMock()
        self.file_mock.__aenter__.return_value = self.file_mock
        self.file_mock.__aexit__ = CoroutineMock()
        self.file_mock.__aexit__.return_value = False
        self.file_mock.read = CoroutineMock()
        self.file_mock.read.return_value = config_data
        self.mock_open.return_value = self.file_mock

    async def test_now(self):
        config = bot.BotConfig()
        await config.read_config()
        self.assertEqual(self.file_mock.read.call_count, 4)
        self.assertIsInstance(config.botnick, str)
        self.assertIsInstance(config.password, str)
        self.assertIsInstance(config.owner, str)
        self.assertIsInstance(config.awsServer, str)
        self.assertIsInstance(config.awsPort, int)
        self.assertIsInstance(config.development, bool)
        self.assertIsInstance(config.messageLimit, int)
        self.assertIsInstance(config.modLimit, int)
        self.assertIsInstance(config.modSpamLimit, int)
        self.assertIsInstance(config.publicLimit, int)
        self.assertIsInstance(config.publicDelay, float)
        self.assertIsInstance(config.messageSpan, float)
        self.assertIsInstance(config.whiperLimit, float)
        self.assertIsInstance(config.whiperSpan, float)
        self.assertIsInstance(config.customMessageCooldown, float)
        self.assertIsInstance(config.customMessageUserCooldown, float)
        self.assertIsInstance(config.customMessageUrlTimeout, float)
        self.assertIsInstance(config.spamModeratorCooldown, float)
        self.assertIsInstance(config.warningDuration, float)
        self.assertIsInstance(config.moderatorDefaultTimeout, list)
        self.assertIsInstance(config.moderatorDefaultTimeout[0], int)
        self.assertIsInstance(config.moderatorDefaultTimeout[1], int)
        self.assertIsInstance(config.moderatorDefaultTimeout[2], int)
        self.assertIsInstance(config.joinLimit, int)
        self.assertIsInstance(config.joinPerSecond, float)
        self.assertIsInstance(config.httpTimeout, float)
        self.assertIsInstance(config.ircLogFolder, str)
        self.assertIsInstance(config.exceptionLog, str)
        self.assertIsInstance(config.database, dict)
        self.assertIsInstance(config.database['main'], str)
        self.assertIsInstance(config.database['oauth'], str)
        self.assertIsInstance(config.database['timeout'], str)
        self.assertIsInstance(config.database['timezone'], str)
        self.mock_mkdir.assert_called_once_with('ircLogs')
