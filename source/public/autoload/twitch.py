import datetime
import ircbot.background
import taskerbot.twitch

ircbot.background.addTask(taskerbot.twitch.checkStreamsAndChannel,
                          datetime.timedelta(seconds=30))
