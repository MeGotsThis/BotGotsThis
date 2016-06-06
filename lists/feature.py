from .public import feature as publicFeature
from collections import ChainMap
try:
    from .private import feature as privateFeature
except ImportError:
    from .private.default import feature as privateFeature

features = ChainMap(privateFeature.features, publicFeature.features)