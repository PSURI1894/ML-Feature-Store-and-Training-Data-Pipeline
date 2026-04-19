"""Feature Platform — a production ML feature store and training data pipeline.

Public surface is intentionally small; import submodules directly, e.g.::

    from feature_platform.training.point_in_time import point_in_time_join
    from feature_platform.online.redis_store import RedisOnlineStore
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
