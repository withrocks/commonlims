"""
sentry.plugins
~~~~~~~~~~~~~~

:copyright: (c) 2010-2014 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from __future__ import absolute_import

HIDDEN_PLUGINS = (
    'bitbucket',
    'gitlab',
    'github',
    'slack',
    'vsts',
    'jira',
    'jira_ac',
)

# TODO: A quick test!!
poor_mans_handler_registry = dict()

from sentry.plugins.base import *  # NOQA
from sentry.plugins.bases import *  # NOQA
from sentry.plugins.interfaces import *  # NOQA
from sentry.plugins.decorators import *  # NOQA
