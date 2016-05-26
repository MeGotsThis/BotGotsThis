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

CustomProcessArgs = namedtuple('CustomProcessArgs',
                               ['database', 'chat', 'tags', 'nick',
                                'permissions', 'broadcaster', 'level',
                                'command', 'messages'])

ManageBotArgs = namedtuple('ManageBotArgs',
                           ['database', 'send', 'nick', 'message'])
