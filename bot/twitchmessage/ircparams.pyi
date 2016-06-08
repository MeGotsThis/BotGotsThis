from typing import List, NamedTuple, Optional

ParsedParams = NamedTuple('ParsedParams',
                          [('middle', Optional[str]),
                           ('trailing', Optional[str])])


class IrcMessageParams:
    def __init__(self,
                 middle:Optional[str]=None,
                 trailing:Optional[str]=None) -> None: ...
    @classmethod
    def fromParams(cls, params:str) -> 'IrcMessageParams': ...
    @property
    def isEmpty(self) -> bool: ...
    @property
    def middle(self) -> Optional[str]: ...
    @property
    def trailing(self) -> Optional[str]: ...
    def __str__(self) -> str: ...
    def __eq__(self, other:object) -> bool: ...
    def __ne__(self, other:object) -> bool: ...
    @staticmethod
    def parse(params:str) -> ParsedParams: ...
