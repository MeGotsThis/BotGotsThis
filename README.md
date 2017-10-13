# BotGotsThis

This is a Twitch.tv bot written by MeGotsThis. The bot is built to have a modular packaging system. This runs on twitch.tv IRC server. The bot has full support for IRC v3 tags. You can read more about it [here](https://dev.twitch.tv/docs/irc)

# Requirements

- [Python 3.6](https://www.python.org/) or higher
- Postgres 9.5 or higher or SQLite 3

# Setup

1. Run pip on requirements.txt
2. Get your OAuth token from [here](https://twitchapps.com/tmi/)
3. Rename any of *.dist.ini to *.ini and fill in any configuration
4. Setting up the database:
    1. Run /lib/database/\*/*.sql to setup the tables to the proper database software
    2. Run /lib/database/gamesabbreviation.sql to populate the game_abbreviations table
5. Run main.py

# Extra modules

Put the extra modules in the pkg folder. Inside the [/pkg](/pkg), there is a folder called base-pkg to help start making your own module. You can find additional modules in my GitHub profile. Afterwards populate pkg.ini in the order of priority and set it to 1 to enable it.

# Tests

Run these commands
- python -m unittest discover -s ./tests/unittest -t ./ -p test_*.py
- python -m unittest discover -s ./pkg -t ./ -p test_*.py
- python -m unittest discover -s ./tests/database -t ./ -p test_*.py
- mypy main.py
- mypy pkg/botgotsthis/mypy-test.py
- mypy pkg/channel/mypy-test.py
- mypy pkg/custom_command/mypy-test.py
- mypy pkg/feature/mypy-test.py
- mypy pkg/moderation/mypy-test.py
- mypy pkg/repeat/mypy-test.py
- mypy pkg/spam/mypy-test.py
- mypy pkg/textformat/mypy-test.py
- mypy pkg/twitch/mypy-test.py
- flake8
  
TODO: making a test script so this doesn't have to be all listed (originally this was less but adding a modular system caused this)
