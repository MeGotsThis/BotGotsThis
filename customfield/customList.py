import customfield.params
import customfield.query
import customfield.url
import customfield.user
try:
    import customprivate.customList as customList
except:
    import customprivate.default.customList as customList

fields = [customfield.user.fieldUser,
          customfield.query.fieldQuery,
          customfield.url.fieldUrl]
fields += customList.fields + [customfield.params.fieldParams]
