import bot
from .store import CacheStore


def get_cache() -> 'CacheStore':
    return CacheStore(bot.globals.redisPool)
