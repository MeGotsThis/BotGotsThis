from collections import namedtuple

ChatCommandArgs = namedtuple('ChatCommandArgs',
                             ['database', 'chat', 'tags', 'nick', 'message',
                              'permissions', 'timestamp',])

WhisperCommandArgs = namedtuple('WhisperCommandArgs',
                                ['database', 'nick', 'message', 'permissions',
                                 'timestamp',])

CustomFieldArgs = namedtuple('CustomFieldArgs',
                             ['field', 'param', 'prefix', 'suffix', 'default',
                              'message', 'channel', 'nick', 'timestamp'])
