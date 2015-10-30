from .public import channel as publicList
try:
    from .private import channel as privateList
except:
    from .private.default import channel as privateList

if privateList.disableFilters:
    filterMessage = privateList.filterMessage
else:
    filterMessage = publicList.filterMessage + privateList.filterMessage
commands = dict(list(publicList.commands.items()) +
                list(privateList.commands.items()))
commandsStartWith = dict(
    list(publicList.commandsStartWith.items()) +
    list(privateList.commandsStartWith.items()))
processNoCommand = privateList.noCommandPreCustom
if not privateList.disableCustomMessage:
    processNoCommand += publicList.processNoCommand
processNoCommand += privateList.noCommandPostCustom
