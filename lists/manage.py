from .public import manage as publicList
try:
    from .private import manage as privateList
except:
    from .private.default import manage as privateList

if False: # Hints for Intellisense
    methods = privateList.methods
    methods = publicList.methods

methods = dict(list(publicList.methods.items()) +
               list(privateList.methods.items()))
