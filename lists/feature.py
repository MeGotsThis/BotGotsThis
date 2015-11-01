from .public import feature as publicFeature
try:
    from .private import feature as privateFeature
except:
    from .private.default import feature as privateFeature

if False: # Hints for Intellisense
    features = privateFeature.features
    features = publicFeature.features

features = dict(list(publicFeature.features.items()) +
                list(privateFeature.features.items()))