from collections import namedtuple

AutoJoinChannel = namedtuple('AutoJoinChannel',
                             ['broadcaster', 'priority', 'cluster'])

CustomCommand = namedtuple('CustomCommand',
                           ['message', 'broadcaster', 'level'])

CustomCommandTokens = namedtuple('CustomCommandTokens',
                                 ['action', 'broadcaster', 'level', 'command',
                                  'text'])

CustomFieldParts = namedtuple('CustomFieldParts',
                              ['plainText', 'field', 'format', 'prefix',
                               'suffix', 'param', 'default', 'original'])
