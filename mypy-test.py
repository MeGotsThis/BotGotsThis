'''
This file is for mypy on checking the background tasks as they are not being
checked as of version 0.4.2.
'''

import bot.globals

import source.public.autoload.twitch
import source.public.autoload.emotes
import source.public.autoload.repeat
import source.private.mypy

import bot.main
import sys
sys.exit(bot.main.main(sys.argv))
