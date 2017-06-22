from datetime import datetime
from tests.database.sqlite.test_database import TestSqlite
from tests.unittest.mock_class import TypeMatch


class TestSqliteCustomCommands(TestSqlite):
    async def setUp(self):
        await super().setUp()
        await self.execute(['''
CREATE TABLE custom_commands (
    broadcaster VARCHAR NOT NULL,
    permission VARCHAR NOT NULL,
    command VARCHAR NOT NULL,
    commandDisplay VARCHAR,
    fullMessage VARCHAR NOT NULL,
    creator VARCHAR,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    lastEditor VARCHAR,
    lastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (broadcaster, permission, command)
)''', '''
CREATE INDEX command_broadcaster ON
    custom_commands (broadcaster, command)''', '''
CREATE TABLE custom_command_properties (
    broadcaster VARCHAR NOT NULL,
    permission VARCHAR NOT NULL,
    command VARCHAR NOT NULL,
    property VARCHAR NOT NULL,
    value VARCHAR NOT NULL,
    PRIMARY KEY (broadcaster, permission, command, property),
    FOREIGN KEY (broadcaster, permission, command)
        REFERENCES custom_commands(broadcaster, permission, command)
        ON DELETE CASCADE ON UPDATE CASCADE
)''', '''
CREATE TABLE custom_commands_history (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    broadcaster VARCHAR NOT NULL,
    permission VARCHAR NOT NULL,
    command VARCHAR NOT NULL,
    commandDisplay VARCHAR,
    process VARCHAR,
    fullMessage VARCHAR,
    creator VARCHAR,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''', '''
CREATE INDEX custom_commands_history_broadcaster ON
    custom_commands_history (broadcaster, command)'''])

    async def test_get_commands(self):
        self.assertEqual(
            await self.database.getChatCommands('botgotsthis', 'kappa'),
            {'#global': {}, 'botgotsthis': {}})

    async def test_get_broadacaster(self):
        now = datetime(2000, 1, 1)
        await self.execute('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           ('botgotsthis', '', 'kappa', None, 'Kappa',
                            'botgotsthis', now, 'botgotsthis', now))
        self.assertEqual(
            await self.database.getChatCommands('botgotsthis', 'kappa'),
            {'#global': {}, 'botgotsthis': {'': 'Kappa'}})

    async def test_get_global(self):
        now = datetime(2000, 1, 1)
        await self.execute('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     ('#global', '', 'kappa', None, 'Kappa', 'botgotsthis',
                      now, 'botgotsthis', now))
        self.assertEqual(
            await self.database.getChatCommands('botgotsthis', 'kappa'),
            {'#global': {'': 'Kappa'}, 'botgotsthis': {}})

    async def test_get_global_broadacaster(self):
        now = datetime(2000, 1, 1)
        await self.executemany('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                         [('botgotsthis', '', 'kappa', None, 'KappaPride',
                           'botgotsthis', now, 'botgotsthis', now),
                          ('#global', '', 'kappa', None, 'KappaRoss',
                           'botgotsthis', now, 'botgotsthis', now),
                          ])
        self.assertEqual(
            await self.database.getChatCommands('botgotsthis', 'kappa'),
            {'#global': {'': 'KappaRoss'},
             'botgotsthis': {'': 'KappaPride'}})

    async def test_get_broadacaster_multi(self):
        now = datetime(2000, 1, 1)
        await self.executemany('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                               [('botgotsthis', '', 'kappa', None, ':O',
                                 'botgotsthis', now, 'botgotsthis', now),
                                ('botgotsthis', 'moderator', 'kappa', None,
                                 ':P', 'botgotsthis', now, 'botgotsthis', now),
                                ('botgotsthis', 'owner', 'kappa', None, ':)',
                                 'botgotsthis', now, 'botgotsthis', now),
                                ])
        self.assertEqual(
            await self.database.getChatCommands('botgotsthis', 'kappa'),
            {'#global': {},
             'botgotsthis': {'': ':O',
                             'moderator': ':P',
                             'owner': ':)'}})

    async def test_get_global_multi(self):
        now = datetime(2000, 1, 1)
        await self.executemany('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                               [('#global', '', 'kappa', None, ':O',
                                 'botgotsthis', now, 'botgotsthis', now),
                                ('#global', 'moderator', 'kappa', None, ':P',
                                 'botgotsthis', now, 'botgotsthis', now),
                                ('#global', 'owner', 'kappa', None, ':)',
                                 'botgotsthis', now, 'botgotsthis', now),
                                ])
        self.assertEqual(
            await self.database.getChatCommands('botgotsthis', 'kappa'),
            {'#global': {'': ':O',
                         'moderator': ':P',
                         'owner': ':)'},
             'botgotsthis': {}})

    async def test_get_broadacaster_global_multi(self):
        now = datetime(2000, 1, 1)
        await self.executemany('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                               [('botgotsthis', '', 'kappa', None, ':O',
                                 'botgotsthis', now, 'botgotsthis', now),
                                ('botgotsthis', 'moderator', 'kappa', None,
                                 ':P', 'botgotsthis', now, 'botgotsthis', now),
                                ('botgotsthis', 'broadcaster', 'kappa', None,
                                 ';)', 'botgotsthis', now, 'botgotsthis', now),
                                ('#global', '', 'kappa', None, ':(',
                                 'botgotsthis', now, 'botgotsthis', now),
                                ('#global', 'admin', 'kappa', None, ':D',
                                 'botgotsthis', now, 'botgotsthis', now),
                                ('#global', 'owner', 'kappa', None, ':)',
                                 'botgotsthis', now, 'botgotsthis', now),
                                ])
        self.assertEqual(
            await self.database.getChatCommands('botgotsthis', 'kappa'),
            {'#global': {'': ':(',
                         'admin': ':D',
                         'owner': ':)'},
             'botgotsthis': {'': ':O',
                             'moderator': ':P',
                             'broadcaster': ';)'}})

    async def test_get_None(self):
        self.assertIsNone(
            await self.database.getCustomCommand('botgotsthis', '', 'kappa'))

    async def test_get(self):
        now = datetime(2000, 1, 1)
        await self.execute('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     ('botgotsthis', '', 'kappa', None, 'Kappa', 'botgotsthis',
                      now, 'botgotsthis', now))
        self.assertEqual(
            await self.database.getCustomCommand('botgotsthis', '', 'kappa'),
            'Kappa')

    async def test_insert(self):
        self.assertIs(
            await self.database.insertCustomCommand(
                'botgotsthis', '', 'kappa', 'KappaHD', 'botgotsthis'),
            True)
        self.assertEqual(
            await self.row('SELECT * FROM custom_commands'),
            ('botgotsthis', '', 'kappa', None, 'KappaHD', 'botgotsthis',
             TypeMatch(datetime), 'botgotsthis', TypeMatch(datetime)))
        self.assertEqual(
            await self.row('SELECT * FROM custom_commands_history'),
            (1, 'botgotsthis', '', 'kappa', None, 'add', 'KappaHD',
             'botgotsthis', TypeMatch(datetime)))

    async def test_insert_commanddisplay(self):
        self.assertIs(
            await self.database.insertCustomCommand(
                'botgotsthis', '', 'Kappa', 'KappaHD', 'botgotsthis'),
            True)
        self.assertEqual(
            await self.row('SELECT * FROM custom_commands'),
            ('botgotsthis', '', 'kappa', 'Kappa', 'KappaHD', 'botgotsthis',
             TypeMatch(datetime), 'botgotsthis', TypeMatch(datetime)))
        self.assertEqual(
            await self.row('SELECT * FROM custom_commands_history'),
            (1, 'botgotsthis', '', 'kappa', 'Kappa', 'add', 'KappaHD',
             'botgotsthis', TypeMatch(datetime)))

    async def test_insert_existing(self):
        now = datetime(2000, 1, 1)
        await self.execute('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           ('botgotsthis', '', 'kappa', None, 'Kappa',
                            'botgotsthis', now, 'botgotsthis', now))
        self.assertIs(
            await self.database.insertCustomCommand(
                'botgotsthis', '', 'kappa', 'KappaHD', 'botgotsthis'),
            False)
        self.assertIsNone(
            await self.row('SELECT * FROM custom_commands_history'))

    async def test_update(self):
        self.assertIs(
            await self.database.updateCustomCommand(
                'botgotsthis', '', 'kappa', 'KappaHD', 'botgotsthis'),
            False)
        self.assertIsNone(await self.row('SELECT * FROM custom_commands'))
        self.assertIsNone(
            await self.row('SELECT * FROM custom_commands_history'))

    async def test_update_existing(self):
        now = datetime(2000, 1, 1)
        await self.execute('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     ('botgotsthis', '', 'kappa', None, 'Kappa', 'botgotsthis',
                      now, 'botgotsthis', now))
        self.assertIs(
            await self.database.updateCustomCommand(
                'botgotsthis', '', 'kappa', 'KappaHD', 'botgotsthis'),
            True)
        self.assertEqual(
            await self.row('SELECT * FROM custom_commands'),
            ('botgotsthis', '', 'kappa', None, 'KappaHD', 'botgotsthis',
             now, 'botgotsthis', TypeMatch(datetime)))
        self.assertEqual(
            await self.row('SELECT * FROM custom_commands_history'),
            (1, 'botgotsthis', '', 'kappa', None, 'edit', 'KappaHD',
             'botgotsthis', TypeMatch(datetime)))

    async def test_update_commanddisplay(self):
        now = datetime(2000, 1, 1)
        await self.execute('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           ('botgotsthis', '', 'kappa', None, 'Kappa',
                            'botgotsthis', now, 'botgotsthis', now))
        self.assertIs(
            await self.database.updateCustomCommand(
                'botgotsthis', '', 'Kappa', 'KappaHD', 'botgotsthis'),
            True)
        self.assertEqual(
            await self.row('SELECT * FROM custom_commands'),
            ('botgotsthis', '', 'kappa', 'Kappa', 'KappaHD', 'botgotsthis',
             now, 'botgotsthis', TypeMatch(datetime)))
        self.assertEqual(
            await self.row('SELECT * FROM custom_commands_history'),
            (1, 'botgotsthis', '', 'kappa', 'Kappa', 'edit', 'KappaHD',
             'botgotsthis', TypeMatch(datetime)))

    async def test_replace(self):
        self.assertIs(
            await self.database.replaceCustomCommand(
                'botgotsthis', '', 'kappa', 'KappaHD', 'botgotsthis'),
            True)
        self.assertEqual(
            await self.row('SELECT * FROM custom_commands'),
            ('botgotsthis', '', 'kappa', None, 'KappaHD', 'botgotsthis',
             TypeMatch(datetime), 'botgotsthis', TypeMatch(datetime)))
        self.assertEqual(
            await self.row('SELECT * FROM custom_commands_history'),
            (1, 'botgotsthis', '', 'kappa', None, 'replace', 'KappaHD',
             'botgotsthis', TypeMatch(datetime)))

    async def test_replace_existing(self):
        now = datetime(2000, 1, 1)
        await self.execute('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           ('botgotsthis', '', 'kappa', None, 'Kappa',
                            'botgotsthis', now, 'botgotsthis', now))
        self.assertIs(
            await self.database.replaceCustomCommand(
                'botgotsthis', '', 'kappa', 'KappaHD', 'botgotsthis'),
            True)
        self.assertEqual(
            await self.rows('SELECT * FROM custom_commands_history'),
            [(1, 'botgotsthis', '', 'kappa', None, 'replace', 'KappaHD',
             'botgotsthis', TypeMatch(datetime))])

    async def test_replace_commanddisplay(self):
        now = datetime(2000, 1, 1)
        await self.execute('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           ('botgotsthis', '', 'kappa', None, 'Kappa',
                            'botgotsthis', now, 'botgotsthis', now))
        self.assertIs(
            await self.database.replaceCustomCommand(
                'botgotsthis', '', 'Kappa', 'KappaHD', 'botgotsthis'),
            True)
        self.assertEqual(
            await self.row('SELECT * FROM custom_commands'),
            ('botgotsthis', '', 'kappa', 'Kappa', 'KappaHD', 'botgotsthis',
             TypeMatch(datetime), 'botgotsthis', TypeMatch(datetime)))
        self.assertEqual(
            await self.row('SELECT * FROM custom_commands_history'),
            (1, 'botgotsthis', '', 'kappa', 'Kappa', 'replace', 'KappaHD',
             'botgotsthis', TypeMatch(datetime)))

    async def test_append(self):
        self.assertIs(
            await self.database.appendCustomCommand(
                'botgotsthis', '', 'kappa', ' Kappa', 'botgotsthis'),
            False)
        self.assertIsNone(
            await self.row('SELECT * FROM custom_commands'))
        self.assertIsNone(
            await self.row('SELECT * FROM custom_commands_history'))

    async def test_append_existing(self):
        now = datetime(2000, 1, 1)
        await self.execute('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           ('botgotsthis', '', 'kappa', None, 'Kappa',
                            'botgotsthis', now, 'botgotsthis', now))
        self.assertIs(
            await self.database.appendCustomCommand(
                'botgotsthis', '', 'kappa', ' Kappa', 'botgotsthis'),
            True)
        self.assertEqual(
            await self.row('SELECT * FROM custom_commands'),
            ('botgotsthis', '', 'kappa', None, 'Kappa Kappa', 'botgotsthis',
             now, 'botgotsthis', TypeMatch(datetime)))
        self.assertEqual(
            await self.row('SELECT * FROM custom_commands_history'),
            (1, 'botgotsthis', '', 'kappa', None, 'append', 'Kappa Kappa',
             'botgotsthis', TypeMatch(datetime)))

    async def test_append_commanddisplay(self):
        now = datetime(2000, 1, 1)
        await self.execute('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           ('botgotsthis', '', 'kappa', None, 'Kappa',
                            'botgotsthis', now, 'botgotsthis', now))
        self.assertIs(
            await self.database.appendCustomCommand(
                'botgotsthis', '', 'Kappa', ' Kappa', 'botgotsthis'),
            True)
        self.assertEqual(
            await self.row('SELECT * FROM custom_commands'),
            ('botgotsthis', '', 'kappa', None, 'Kappa Kappa', 'botgotsthis',
             now, 'botgotsthis', TypeMatch(datetime)))
        self.assertEqual(
            await self.row('SELECT * FROM custom_commands_history'),
            (1, 'botgotsthis', '', 'kappa', 'Kappa', 'append', 'Kappa Kappa',
             'botgotsthis', TypeMatch(datetime)))

    async def test_delete(self):
        self.assertIs(
            await self.database.deleteCustomCommand(
                'botgotsthis', '', 'kappa', 'botgotsthis'),
            False)
        self.assertIsNone(await self.row('SELECT * FROM custom_commands'))
        self.assertIsNone(
            await self.row('SELECT * FROM custom_commands_history'))

    async def test_delete_existing(self):
        now = datetime(2000, 1, 1)
        await self.execute('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     ('botgotsthis', '', 'kappa', None, 'Kappa', 'botgotsthis',
                      now, 'botgotsthis', now))
        await self.execute('''
INSERT INTO custom_command_properties VALUES (?, ?, ?, ?, ?)''',
                     ('botgotsthis', '', 'kappa', 'kappa', 'Kappa'))
        self.assertIs(
            await self.database.deleteCustomCommand(
                'botgotsthis', '', 'kappa', 'botgotsthis'),
            True)
        self.assertIsNone(await self.row('SELECT * FROM custom_commands'))
        self.assertIsNone(
            await self.row('SELECT * FROM custom_command_properties'))
        self.assertEqual(
            await self.row('SELECT * FROM custom_commands_history'),
            (1, 'botgotsthis', '', 'kappa', None, 'delete', None,
             'botgotsthis', TypeMatch(datetime)))

    async def test_delete_commanddisplay(self):
        now = datetime(2000, 1, 1)
        await self.execute('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           ('botgotsthis', '', 'kappa', None, 'Kappa',
                            'botgotsthis', now, 'botgotsthis', now))
        self.assertIs(
            await self.database.deleteCustomCommand(
                'botgotsthis', '', 'Kappa', 'botgotsthis'),
            True)
        self.assertIsNone(await self.row('SELECT * FROM custom_commands'))
        self.assertEqual(
            await self.row('SELECT * FROM custom_commands_history'),
            (1, 'botgotsthis', '', 'kappa', 'Kappa', 'delete', None,
             'botgotsthis', TypeMatch(datetime)))

    async def test_level(self):
        self.assertIs(
            await self.database.levelCustomCommand(
                'botgotsthis', '', 'kappa', 'botgotsthis', 'moderator'),
            False)
        self.assertIsNone(await self.row('SELECT * FROM custom_commands'))
        self.assertIsNone(
            await self.row('SELECT * FROM custom_commands_history'))

    async def test_level_existing(self):
        now = datetime(2000, 1, 1)
        await self.execute('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           ('botgotsthis', '', 'kappa', None, 'Kappa',
                            'botgotsthis', now, 'botgotsthis', now))
        await self.execute('''
INSERT INTO custom_command_properties VALUES (?, ?, ?, ?, ?)''',
                           ('botgotsthis', '', 'kappa', 'kappa', 'Kappa'))
        self.assertIs(
            await self.database.levelCustomCommand(
                'botgotsthis', '', 'kappa', 'botgotsthis', 'moderator'),
            True)
        self.assertEqual(
            await self.row('SELECT * FROM custom_commands'),
            ('botgotsthis', 'moderator', 'kappa', None, 'Kappa', 'botgotsthis',
             now, 'botgotsthis', TypeMatch(datetime)))
        self.assertEqual(
            await self.row('SELECT * FROM custom_command_properties'),
            ('botgotsthis', 'moderator', 'kappa', 'kappa', 'Kappa'))
        self.assertEqual(
            await self.row('SELECT * FROM custom_commands_history'),
            (1, 'botgotsthis', 'moderator', 'kappa', None, 'level', '',
             'botgotsthis', TypeMatch(datetime)))

    async def test_level_overlap(self):
        now = datetime(2000, 1, 1)
        await self.executemany('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                         [('botgotsthis', '', 'kappa', None, 'Kappa',
                           'botgotsthis', now, 'botgotsthis', now),
                          ('botgotsthis', 'moderator', 'kappa', None, 'Kappa',
                           'botgotsthis', now, 'botgotsthis', now)])
        await self.execute('''
INSERT INTO custom_command_properties VALUES (?, ?, ?, ?, ?)''',
                           ('botgotsthis', '', 'kappa', 'kappa', 'Kappa'))
        self.assertIs(
            await self.database.levelCustomCommand(
                'botgotsthis', '', 'kappa', 'botgotsthis', 'moderator'),
            False)
        self.assertEqual(
            await self.rows('SELECT * FROM custom_commands'),
            [('botgotsthis', '', 'kappa', None, 'Kappa', 'botgotsthis',
              now, 'botgotsthis', now),
             ('botgotsthis', 'moderator', 'kappa', None, 'Kappa',
              'botgotsthis', now, 'botgotsthis', now)])
        self.assertEqual(
            await self.row('SELECT * FROM custom_command_properties'),
            ('botgotsthis', '', 'kappa', 'kappa', 'Kappa'))

    async def test_level_commanddisplay(self):
        now = datetime(2000, 1, 1)
        await self.execute('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     ('botgotsthis', '', 'kappa', None, 'Kappa', 'botgotsthis',
                      now, 'botgotsthis', now))
        self.assertIs(
            await self.database.levelCustomCommand(
                'botgotsthis', '', 'Kappa', 'botgotsthis', 'moderator'),
            True)
        self.assertEqual(
            await self.row('SELECT * FROM custom_commands'),
            ('botgotsthis', 'moderator', 'kappa', None, 'Kappa', 'botgotsthis',
             now, 'botgotsthis', TypeMatch(datetime)))
        self.assertEqual(
            await self.row('SELECT * FROM custom_commands_history'),
            (1, 'botgotsthis', 'moderator', 'kappa', 'Kappa', 'level', '',
             'botgotsthis', TypeMatch(datetime)))

    async def test_rename(self):
        self.assertIs(
            await self.database.renameCustomCommand(
                'botgotsthis', '', 'kappa', 'botgotsthis', 'pogchamp'),
            False)
        self.assertIsNone(await self.row('SELECT * FROM custom_commands'))
        self.assertIsNone(
            await self.row('SELECT * FROM custom_commands_history'))

    async def test_rename_existing(self):
        now = datetime(2000, 1, 1)
        await self.execute('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           ('botgotsthis', '', 'kappa', None, 'Kappa',
                            'botgotsthis', now, 'botgotsthis', now))
        await self.execute('''
INSERT INTO custom_command_properties VALUES (?, ?, ?, ?, ?)''',
                     ('botgotsthis', '', 'kappa', 'kappa', 'Kappa'))
        self.assertIs(
            await self.database.renameCustomCommand(
                'botgotsthis', '', 'kappa', 'botgotsthis', 'pogchamp'),
            True)
        self.assertEqual(
            await self.row('SELECT * FROM custom_commands'),
            ('botgotsthis', '', 'pogchamp', None, 'Kappa', 'botgotsthis',
             now, 'botgotsthis', TypeMatch(datetime)))
        self.assertEqual(
            await self.row('SELECT * FROM custom_command_properties'),
            ('botgotsthis', '', 'pogchamp', 'kappa', 'Kappa'))
        self.assertEqual(
            await self.row('SELECT * FROM custom_commands_history'),
            (1, 'botgotsthis', '', 'pogchamp', None, 'rename', 'kappa',
             'botgotsthis', TypeMatch(datetime)))

    async def test_rename_overlap(self):
        now = datetime(2000, 1, 1)
        await self.executemany('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                               [('botgotsthis', '', 'kappa', None, 'Kappa',
                                 'botgotsthis', now, 'botgotsthis', now),
                                ('botgotsthis', '', 'pogchamp', None,
                                 'PogChamp', 'botgotsthis', now, 'botgotsthis',
                                 now)])
        await self.execute('''
INSERT INTO custom_command_properties VALUES (?, ?, ?, ?, ?)''',
                           ('botgotsthis', '', 'pogchamp', 'kappa', 'Kappa'))
        self.assertIs(
            await self.database.renameCustomCommand(
                'botgotsthis', '', 'kappa', 'botgotsthis', 'pogchamp'),
            False)
        self.assertEqual(
            await self.rows('SELECT * FROM custom_commands'),
            [('botgotsthis', '', 'kappa', None, 'Kappa', 'botgotsthis',
              now, 'botgotsthis', now),
             ('botgotsthis', '', 'pogchamp', None, 'PogChamp', 'botgotsthis',
              now, 'botgotsthis', now)])
        self.assertEqual(
            await self.row('SELECT * FROM custom_command_properties'),
            ('botgotsthis', '', 'pogchamp', 'kappa', 'Kappa'))

    async def test_rename_commanddisplay(self):
        now = datetime(2000, 1, 1)
        await self.execute('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     ('botgotsthis', '', 'kappa', None, 'Kappa', 'botgotsthis',
                      now, 'botgotsthis', now))
        self.assertIs(
            await self.database.renameCustomCommand(
                'botgotsthis', '', 'Kappa', 'botgotsthis', 'PogChamp'),
            True)
        self.assertEqual(
            await self.row('SELECT * FROM custom_commands'),
            ('botgotsthis', '', 'pogchamp', 'PogChamp', 'Kappa', 'botgotsthis',
             now, 'botgotsthis', TypeMatch(datetime)))
        self.assertEqual(
            await self.row('SELECT * FROM custom_commands_history'),
            (1, 'botgotsthis', '', 'pogchamp', 'PogChamp', 'rename', 'kappa',
             'botgotsthis', TypeMatch(datetime)))

    async def test_get_property_no_command(self):
        self.assertIsNone(
            await self.database.getCustomCommandProperty(
                'botgotsthis', '', 'kappa', 'something'))

    async def test_get_property_nothing(self):
        now = datetime(2000, 1, 1)
        await self.execute('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           ('botgotsthis', '', 'kappa', None, 'Kappa',
                            'botgotsthis',
                            now, 'botgotsthis', now))
        self.assertIsNone(
            await self.database.getCustomCommandProperty(
                'botgotsthis', '', 'kappa', 'something'))

    async def test_get_property_str(self):
        now = datetime(2000, 1, 1)
        await self.execute('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           ('botgotsthis', '', 'kappa', None, 'Kappa',
                            'botgotsthis', now, 'botgotsthis', now))
        await self.execute('''
INSERT INTO custom_command_properties VALUES (?, ?, ?, ?, ?)''',
                           ('botgotsthis', '', 'kappa', 'kappa', 'Kappa'))
        self.assertEqual(
            await self.database.getCustomCommandProperty(
                'botgotsthis', '', 'kappa', 'kappa'),
            'Kappa')

    async def test_get_property_list(self):
        now = datetime(2000, 1, 1)
        await self.execute('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           ('botgotsthis', '', 'kappa', None, 'Kappa',
                            'botgotsthis', now, 'botgotsthis', now))
        await self.execute('''
INSERT INTO custom_command_properties VALUES (?, ?, ?, ?, ?)''',
                           ('botgotsthis', '', 'kappa', 'kappa', 'Kappa'))
        await self.execute('''
INSERT INTO custom_command_properties VALUES (?, ?, ?, ?, ?)''',
                           ('botgotsthis', '', 'kappa', 'kappaross',
                            'KappaRoss'))
        await self.execute('''
INSERT INTO custom_command_properties VALUES (?, ?, ?, ?, ?)''',
                           ('botgotsthis', '', 'kappa', 'kappapride',
                            'KappaPride'))
        self.assertEqual(
            await self.database.getCustomCommandProperty(
                'botgotsthis', '', 'kappa', ['kappaross', 'kappapride']),
            {'kappaross': 'KappaRoss', 'kappapride': 'KappaPride'})

    async def test_get_property_all(self):
        now = datetime(2000, 1, 1)
        await self.execute('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           ('botgotsthis', '', 'kappa', None, 'Kappa',
                            'botgotsthis', now, 'botgotsthis', now))
        await self.execute('''
INSERT INTO custom_command_properties VALUES (?, ?, ?, ?, ?)''',
                           ('botgotsthis', '', 'kappa', 'kappa', 'Kappa'))
        await self.execute('''
INSERT INTO custom_command_properties VALUES (?, ?, ?, ?, ?)''',
                           ('botgotsthis', '', 'kappa', 'kappaross',
                            'KappaRoss'))
        await self.execute('''
INSERT INTO custom_command_properties VALUES (?, ?, ?, ?, ?)''',
                           ('botgotsthis', '', 'kappa', 'kappapride',
                            'KappaPride'))
        self.assertEqual(
            await self.database.getCustomCommandProperty(
                'botgotsthis', '', 'kappa'),
            {'kappa': 'Kappa', 'kappaross': 'KappaRoss',
             'kappapride': 'KappaPride'})

    async def test_process_property_no_command(self):
        self.assertIs(
            await self.database.processCustomCommandProperty(
                'botgotsthis', '', 'kappa', 'kappa', 'Kappa'),
            False)
        self.assertIsNone(
            await self.row('SELECT * FROM custom_command_properties'))

    async def test_process_property(self):
        now = datetime(2000, 1, 1)
        await self.execute('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     ('botgotsthis', '', 'kappa', None, 'Kappa', 'botgotsthis',
                      now, 'botgotsthis', now))
        self.assertIs(
            await self.database.processCustomCommandProperty(
                'botgotsthis', '', 'kappa', 'kappa', 'Kappa'),
            True)
        self.assertEqual(
            await self.row('SELECT * FROM custom_command_properties'),
            ('botgotsthis', '', 'kappa', 'kappa', 'Kappa'))

    async def test_process_property_change(self):
        now = datetime(2000, 1, 1)
        await self.execute('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     ('botgotsthis', '', 'kappa', None, 'Kappa', 'botgotsthis',
                      now, 'botgotsthis', now))
        await self.execute('''
INSERT INTO custom_command_properties VALUES (?, ?, ?, ?, ?)''',
                     ('botgotsthis', '', 'kappa', 'kappa', 'PogChamp'))
        self.assertIs(
            await self.database.processCustomCommandProperty(
                'botgotsthis', '', 'kappa', 'kappa', 'Kappa'),
            True)
        self.assertEqual(
            await self.row('SELECT * FROM custom_command_properties'),
            ('botgotsthis', '', 'kappa', 'kappa', 'Kappa'))

    async def test_process_property_delete(self):
        now = datetime(2000, 1, 1)
        await self.execute('''
INSERT INTO custom_commands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     ('botgotsthis', '', 'kappa', None, 'Kappa', 'botgotsthis',
                      now, 'botgotsthis', now))
        await self.execute('''
INSERT INTO custom_command_properties VALUES (?, ?, ?, ?, ?)''',
                     ('botgotsthis', '', 'kappa', 'kappa', 'PogChamp'))
        self.assertIs(
            await self.database.processCustomCommandProperty(
                'botgotsthis', '', 'kappa', 'kappa'),
            True)
        self.assertIsNone(
            await self.row('SELECT * FROM custom_command_properties'))
