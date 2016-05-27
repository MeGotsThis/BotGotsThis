from collections import namedtuple

AutoJoinChannel = namedtuple('AutoJoinChannel',
                             ['broadcaster', 'priority', 'cluster'])

CustomCommandTokens = namedtuple('CustomCommandTokens',
                                 ['called', 'action', 'level', 'command',
                                  'text'])
