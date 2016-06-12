from .public import feature as publicFeature
from collections import ChainMap
from typing import Mapping, Optional
try:
    from .private import feature as privateFeature
except ImportError:
    from .private.default import feature as privateFeature  # type: ignore

FeatureDict = Mapping[str, Optional[str]]

features = ChainMap(privateFeature.features, publicFeature.features)  # type: FeatureDict
