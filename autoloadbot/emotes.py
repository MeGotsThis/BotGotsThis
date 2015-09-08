import datetime
import ircbot.background
import taskerbot.emotes

ircbot.background.addTask(taskerbot.emotes.refreshTwitchGlobalEmotes,
                          datetime.timedelta(seconds=1))
ircbot.background.addTask(taskerbot.emotes.refreshTwitchGlobalEmotes,
                          datetime.timedelta(milliseconds=.75))
