from typing import NamedTuple, Union

AutoJoinChannel = NamedTuple('AutoJoinChannel',
                             [('broadcaster', str),
                              ('priority', Union[int, float]),
                              ('cluster', str)])

CustomCommand = NamedTuple('CustomCommand',
                           [('message', str),
                            ('broadcaster', str),
                            ('level', str)])

CustomCommandTokens = NamedTuple('CustomCommandTokens',
                                 [('action', str),
                                  ('broadcaster', str),
                                  ('level', str),
                                  ('command', str),
                                  ('text', str)])

CustomFieldParts = NamedTuple('CustomFieldParts',
                              [('plainText', str),
                               ('field', str),
                               ('format', str),
                               ('prefix', str),
                               ('suffix', str),
                               ('param', str),
                               ('default', str),
                               ('original', str)])
