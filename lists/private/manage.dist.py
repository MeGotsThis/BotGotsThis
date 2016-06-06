from source.data.argument import ManageBotArgs
from typing import Callable, Mapping, Optional

methods = {}  # type: Mapping[str, Optional[Callable[[ManageBotArgs], bool]]]
