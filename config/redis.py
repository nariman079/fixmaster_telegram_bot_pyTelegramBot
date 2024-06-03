import pickle

import redis

cache = redis.Redis(
    host='localhost',
)


def dict_set(name: str, data: dict):
    cache.set(name, pickle.dumps(data))


def dict_get(name: str) -> dict:
    if value := cache.get(name):
        return pickle.loads(value)
