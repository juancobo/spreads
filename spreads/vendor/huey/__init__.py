from .api import Huey, crontab
try:
    import redis
    from .backends.redis_backend import RedisBlockingQueue
    from .backends.redis_backend import RedisDataStore
    from .backends.redis_backend import RedisEventEmitter
    from .backends.redis_backend import RedisSchedule

    class RedisHuey(Huey):
        def __init__(self, name='huey', store_none=False, always_eager=False,
                     **conn_kwargs):
            queue = RedisBlockingQueue(name, **conn_kwargs)
            result_store = RedisDataStore(name, **conn_kwargs)
            schedule = RedisSchedule(name, **conn_kwargs)
            events = RedisEventEmitter(name, **conn_kwargs)
            super(RedisHuey, self).__init__(
                queue=queue,
                result_store=result_store,
                schedule=schedule,
                events=events,
                store_none=store_none,
                always_eager=always_eager)

except ImportError:
    class RedisHuey(object):
        def __init__(self, *args, **kwargs):
            raise RuntimeError('Error, "redis" is not installed. Install '
                               'using pip: "pip install redis"')


from .backends.sqlite_backend import SqliteQueue
from .backends.sqlite_backend import SqliteDataStore
from .backends.sqlite_backend import SqliteEventEmitter
from .backends.sqlite_backend import SqliteSchedule


class SqliteHuey(Huey):
    def __init__(self, name='huey', store_none=False, always_eager=False,
                 location=None):
        if location is None:
            raise ValueError("Please specify a database file with the "
                             "'location' parameter")
        queue = SqliteQueue(name, location)
        result_store = SqliteDataStore(name, location)
        schedule = SqliteSchedule(name, location)
        events = SqliteEventEmitter(name, location=location)
        super(SqliteHuey, self).__init__(
            queue=queue,
            result_store=result_store,
            schedule=schedule,
            events=events,
            store_none=store_none,
            always_eager=always_eager)
