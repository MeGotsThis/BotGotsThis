from typing import NamedTuple, Optional, Union

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
                               ('field', Optional[str]),
                               ('format', Optional[str]),
                               ('prefix', Optional[str]),
                               ('suffix', Optional[str]),
                               ('param', Optional[str]),
                               ('default', Optional[str]),
                               ('original', Optional[str])])
