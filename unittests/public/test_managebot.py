import unittest
from datetime import datetime
from source.data import ManageBotArgs
from source.data.message import Message
from source.database import DatabaseBase
from unittest.mock import Mock


def send(messages):
    pass


class TestManageBot(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2000, 1, 1)
        self.send = Mock(spec=send)
        self.database = Mock(spec=DatabaseBase)
        self.args = ManageBotArgs(self.database, self.send, 'botgotsthis',
                                  Message(''))
