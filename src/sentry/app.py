"""
sentry.app
~~~~~~~~~~

:copyright: (c) 2010-2014 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from __future__ import absolute_import

from threading import local

from sentry.utils import redis
from sentry.utils.locking.backends.redis import RedisLockBackend
from sentry.utils.locking.manager import LockManager


class State(local):
    request = None
    data = {}


env = State()


# COMPAT
from sentry import search, tsdb  # NOQA
from .buffer import backend as buffer  # NOQA
from .digests import backend as digests  # NOQA
from .quotas import backend as quotas  # NOQA
from .ratelimits import backend as ratelimiter  # NOQA

from sentry.utils.sdk import RavenShim

raven = client = RavenShim()  # NOQA

locks = LockManager(RedisLockBackend(redis.clusters.get('default')))
