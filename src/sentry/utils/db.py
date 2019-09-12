"""
sentry.utils.db
~~~~~~~~~~~~~~~

:copyright: (c) 2010-2014 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from __future__ import absolute_import

import six
from contextlib import contextmanager, closing

from django.conf import settings
from django.db import connections, DEFAULT_DB_ALIAS
from django.db.models.fields.related_descriptors import ReverseOneToOneDescriptor


def get_db_engine(alias='default'):
    value = settings.DATABASES[alias]['ENGINE']
    if value == 'mysql.connector.django':
        return 'mysql'
    return value.rsplit('.', 1)[-1]


def is_postgres(alias='default'):
    engine = get_db_engine(alias)
    return 'postgres' in engine


def is_mysql(alias='default'):
    engine = get_db_engine(alias)
    return 'mysql' in engine


def is_sqlite(alias='default'):
    engine = get_db_engine(alias)
    return 'sqlite' in engine


def has_charts(db):
    if is_sqlite(db):
        return False
    return True


def attach_foreignkey(objects, field):
    """
    Shortcut method which handles a pythonic LEFT OUTER JOIN.

    ``attach_foreignkey(posts, Post.thread)``

    Works with both ForeignKey and OneToOne (reverse) lookups.
    """
    related = []

    if not objects:
        return

    database = list(objects)[0]._state.db

    is_foreignkey = isinstance(field, ReverseOneToOneDescriptor)

    if not is_foreignkey:
        field = field.field
        accessor = '_%s_cache' % field.name
        model = field.rel.to
        lookup = 'pk'
        column = field.column
        key = lookup
    else:
        accessor = field.cache_name
        field = field.related.field
        model = field.model
        lookup = field.name
        column = 'pk'
        key = field.column

    objects = [o for o in objects if (related or getattr(o, accessor, False) is False)]

    if not objects:
        return

    # Ensure values are unique, do not contain already present values, and are not missing
    # values specified in select_related
    values = set(filter(None, (getattr(o, column) for o in objects)))
    if values:
        qs = model.objects
        if database:
            qs = qs.using(database)
        if related:
            qs = qs.select_related(*related)

        if len(values) > 1:
            qs = qs.filter(**{'%s__in' % lookup: values})
        else:
            qs = [qs.get(**{lookup: six.next(iter(values))})]

        queryset = dict((getattr(o, key), o) for o in qs)
    else:
        queryset = {}

    for o in objects:
        setattr(o, accessor, queryset.get(getattr(o, column)))


def table_exists(name, using=DEFAULT_DB_ALIAS):
    return name in connections[using].introspection.table_names()


def _set_mysql_foreign_key_checks(flag, using=DEFAULT_DB_ALIAS):
    if is_mysql():
        query = 'SET FOREIGN_KEY_CHECKS=%s' % (1 if flag else 0)
        with closing(connections[using].cursor()) as cursor:
            cursor.execute(query)


@contextmanager
def mysql_disabled_integrity(db=DEFAULT_DB_ALIAS):
    try:
        _set_mysql_foreign_key_checks(False, using=db)
        yield
    finally:
        _set_mysql_foreign_key_checks(True, using=db)
