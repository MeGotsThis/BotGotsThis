from collections import namedtuple

ChatCommandArgs = namedtuple('ChatCommandArgs',
                             ['database', 'chat', 'tags', 'nick', 'message',
                              'permissions', 'timestamp',])
