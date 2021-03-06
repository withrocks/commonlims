"""
sentry.runner.initializer
~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2015 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from __future__ import absolute_import, print_function

import click
import os
import six
import logging

from sentry.utils import warnings
from sentry.utils.warnings import DeprecatedSettingWarning

logger = logging.getLogger(__name__)


def initialize_receivers():
    # force signal registration
    import sentry.receivers  # NOQA


def get_asset_version(settings):
    path = os.path.join(settings.STATIC_ROOT, 'version')
    try:
        with open(path) as fp:
            return fp.read().strip()
    except IOError:
        from time import time
        return int(time())


# Options which must get extracted into Django settings while
# bootstrapping. Everything else will get validated and used
# as a part of OptionsManager.
options_mapper = {
    # 'cache.backend': 'SENTRY_CACHE',
    # 'cache.options': 'SENTRY_CACHE_OPTIONS',
    # 'system.databases': 'DATABASES',
    # 'system.debug': 'DEBUG',
    'system.secret-key': 'SECRET_KEY',
    'mail.backend': 'EMAIL_BACKEND',
    'mail.host': 'EMAIL_HOST',
    'mail.port': 'EMAIL_PORT',
    'mail.username': 'EMAIL_HOST_USER',
    'mail.password': 'EMAIL_HOST_PASSWORD',
    'mail.use-tls': 'EMAIL_USE_TLS',
    'mail.from': 'SERVER_EMAIL',
    'mail.subject-prefix': 'EMAIL_SUBJECT_PREFIX',
}


def bootstrap_options(settings, config=None):
    """
    Quickly bootstrap options that come in from a config file
    and convert options into Django settings that are
    required to even initialize the rest of the app.
    """
    # Make sure our options have gotten registered
    from sentry.options import load_defaults
    load_defaults()

    options = {}
    if config is not None:
        # Attempt to load our config yaml file
        from sentry.utils.yaml import safe_load
        from yaml.parser import ParserError
        from yaml.scanner import ScannerError
        try:
            with open(config, 'rb') as fp:
                options = safe_load(fp)
        except IOError:
            # Gracefully fail if yaml file doesn't exist
            pass
        except (AttributeError, ParserError, ScannerError) as e:
            from .importer import ConfigurationError
            raise ConfigurationError('Malformed config.yml file: %s' % six.text_type(e))

        # Empty options file, so fail gracefully
        if options is None:
            options = {}
        # Options needs to be a dict
        elif not isinstance(options, dict):
            from .importer import ConfigurationError
            raise ConfigurationError('Malformed config.yml file')

    from sentry.conf.server import DEAD

    # First move options from settings into options
    for k, v in six.iteritems(options_mapper):
        if getattr(settings, v, DEAD) is not DEAD and k not in options:
            warnings.warn(
                DeprecatedSettingWarning(
                    options_mapper[k],
                    "SENTRY_OPTIONS['%s']" % k,
                )
            )
            options[k] = getattr(settings, v)

    # Stuff everything else into SENTRY_OPTIONS
    # these will be validated later after bootstrapping
    for k, v in six.iteritems(options):
        settings.SENTRY_OPTIONS[k] = v

    # Now go back through all of SENTRY_OPTIONS and promote
    # back into settings. This catches the case when values are defined
    # only in SENTRY_OPTIONS and no config.yml file
    for o in (settings.SENTRY_DEFAULT_OPTIONS, settings.SENTRY_OPTIONS):
        for k, v in six.iteritems(o):
            if k in options_mapper:
                # Map the mail.backend aliases to something Django understands
                if k == 'mail.backend':
                    try:
                        v = settings.SENTRY_EMAIL_BACKEND_ALIASES[v]
                    except KeyError:
                        pass
                # Escalate the few needed to actually get the app bootstrapped into settings
                setattr(settings, options_mapper[k], v)


def initialize_app(config, skip_service_validation=False):
    settings = config['settings']

    bootstrap_options(settings, config['options'])

    from clims.logs import configure_logging
    configure_logging()

    if 'south' in settings.INSTALLED_APPS:
        fix_south(settings)

    # Commonly setups don't correctly configure themselves for production envs
    # so lets try to provide a bit more guidance
    if settings.CELERY_ALWAYS_EAGER and not settings.DEBUG:
        warnings.warn(
            'Sentry is configured to run asynchronous tasks in-process. '
            'This is not recommended within production environments. '
            'See https://docs.sentry.io/on-premise/server/queue/ for more information.'
        )

    if settings.SENTRY_SINGLE_ORGANIZATION:
        settings.SENTRY_FEATURES['organizations:create'] = False

    if not hasattr(settings, 'SUDO_COOKIE_SECURE'):
        settings.SUDO_COOKIE_SECURE = getattr(settings, 'SESSION_COOKIE_SECURE', False)
    if not hasattr(settings, 'SUDO_COOKIE_DOMAIN'):
        settings.SUDO_COOKIE_DOMAIN = getattr(settings, 'SESSION_COOKIE_DOMAIN', None)
    if not hasattr(settings, 'SUDO_COOKIE_PATH'):
        settings.SUDO_COOKIE_PATH = getattr(settings, 'SESSION_COOKIE_PATH', '/')

    if not hasattr(settings, 'CSRF_COOKIE_SECURE'):
        settings.CSRF_COOKIE_SECURE = getattr(settings, 'SESSION_COOKIE_SECURE', False)
    if not hasattr(settings, 'CSRF_COOKIE_DOMAIN'):
        settings.CSRF_COOKIE_DOMAIN = getattr(settings, 'SESSION_COOKIE_DOMAIN', None)
    if not hasattr(settings, 'CSRF_COOKIE_PATH'):
        settings.CSRF_COOKIE_PATH = getattr(settings, 'SESSION_COOKIE_PATH', '/')

    settings.CACHES['default']['VERSION'] = settings.CACHE_VERSION

    settings.ASSET_VERSION = get_asset_version(settings)
    settings.STATIC_URL = settings.STATIC_URL.format(
        version=settings.ASSET_VERSION,
    )

    import django
    django.setup()

    bind_cache_to_option_store()

    from clims.services.application import ioc, ApplicationService
    app = ApplicationService()
    ioc.set_application(app)
    app.plugins.load_installed()

    initialize_receivers()

    validate_options(settings)

    setup_services(validate=not skip_service_validation)

    from django.utils import timezone
    from sentry.app import env
    from sentry.runner.settings import get_sentry_conf
    env.data['config'] = get_sentry_conf()
    env.data['start_date'] = timezone.now()


def setup_services(validate=True):
    from sentry import (
        analytics, buffer, digests, newsletter, quotas,
        ratelimits, search, tagstore, tsdb
    )
    from .importer import ConfigurationError
    from sentry.utils.settings import reraise_as

    service_list = (
        analytics, buffer, digests, newsletter, quotas,
        ratelimits, search, tagstore, tsdb,
    )

    for service in service_list:
        if validate:
            try:
                service.validate()
            except AttributeError as exc:
                reraise_as(
                    ConfigurationError(
                        u'{} service failed to call validate()\n{}'.format(
                            service.__name__,
                            six.text_type(exc),
                        )
                    )
                )
        try:
            service.setup()
        except AttributeError as exc:
            if not hasattr(service, 'setup') or not callable(service.setup):
                reraise_as(
                    ConfigurationError(
                        u'{} service failed to call setup()\n{}'.format(
                            service.__name__,
                            six.text_type(exc),
                        )
                    )
                )
            raise


def validate_options(settings):
    from sentry.options import default_manager
    default_manager.validate(settings.SENTRY_OPTIONS, warn=True)


def fix_south(settings):
    settings.SOUTH_DATABASE_ADAPTERS = {}

    # South needs an adapter defined conditionally
    for key, value in six.iteritems(settings.DATABASES):
        if value['ENGINE'] != 'sentry.db.postgres':
            continue
        settings.SOUTH_DATABASE_ADAPTERS[key] = 'south.db.postgresql_psycopg2'


def bind_cache_to_option_store():
    # The default ``OptionsStore`` instance is initialized without the cache
    # backend attached. The store itself utilizes the cache during normal
    # operation, but can't use the cache before the options (which typically
    # includes the cache configuration) have been bootstrapped from the legacy
    # settings and/or configuration values. Those options should have been
    # loaded at this point, so we can plug in the cache backend before
    # continuing to initialize the remainder of the application.
    from django.core.cache import cache as default_cache
    from sentry.options import default_store

    default_store.cache = default_cache


def show_big_error(message):
    if isinstance(message, six.string_types):
        lines = message.splitlines()
    else:
        lines = message
    maxline = max(map(len, lines))
    click.echo('', err=True)
    click.secho('!! %s !!' % ('!' * min(maxline, 80), ), err=True, fg='red')
    for line in lines:
        click.secho('!! %s !!' % line.center(maxline), err=True, fg='red')
    click.secho('!! %s !!' % ('!' * min(maxline, 80), ), err=True, fg='red')
    click.echo('', err=True)


def skip_migration_if_applied(settings, app_name, table_name, name='0001_initial'):
    from south.migration import Migrations
    from sentry.utils.db import table_exists
    import types

    if app_name not in settings.INSTALLED_APPS:
        return

    migration = Migrations(app_name)[name]

    def skip_if_table_exists(original):
        def wrapped(self):
            # TODO: look into why we're having to return some ridiculous
            # lambda
            if table_exists(table_name):
                return lambda x=None: None
            return original()

        wrapped.__name__ = original.__name__
        return wrapped

    migration.forwards = types.MethodType(skip_if_table_exists(migration.forwards), migration)


def on_configure(config):
    """
    Executes after settings are full installed and configured.

    At this point we can force import on various things such as models
    as all of settings should be correctly configured.
    """
    settings = config['settings']

    if 'south' in settings.INSTALLED_APPS:
        skip_migration_if_applied(settings, 'social_auth', 'social_auth_association')
