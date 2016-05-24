from .public import feature as publicFeature
from collections import ChainMap
try:
    from .private import feature as privateFeature
except:
    from .private.default import feature as privateFeature

if False: # Hints for Intellisense
    features = privateFeature.features
    features = publicFeature.features

features = ChainMap(privateFeature.features, publicFeature.features)