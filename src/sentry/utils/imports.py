"""
sentry.utils.imports
~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2014 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from __future__ import absolute_import

import pkgutil
import six


MODEL_MOVES = {
    'sentry.models.tagkey.TagKey': 'sentry.tagstore.legacy.models.tagkey.TagKey',
    'sentry.models.tagvalue.tagvalue': 'sentry.tagstore.legacy.models.tagvalue.TagValue',
    'sentry.models.grouptagkey.GroupTagKey': 'sentry.tagstore.legacy.models.grouptagkey.GroupTagKey',
    'sentry.models.grouptagvalue.GroupTagValue': 'sentry.tagstore.legacy.models.grouptagvalue.GroupTagValue',
    'sentry.models.eventtag.EventTag': 'sentry.tagstore.legacy.models.eventtag.EventTag',
}


class ModuleProxyCache(dict):
    def __missing__(self, key):
        if '.' not in key:
            return __import__(key)

        module_name, class_name = key.rsplit('.', 1)

        module = __import__(module_name, {}, {}, [class_name])
        handler = getattr(module, class_name)

        # We cache a NoneType for missing imports to avoid repeated lookups
        self[key] = handler

        return handler


_cache = ModuleProxyCache()


def import_string(path):
    """
    Path must be module.path.ClassName

    >>> cls = import_string('sentry.models.Group')
    """
    path = MODEL_MOVES.get(path, path)
    result = _cache[path]
    return result


def import_submodules(context, root_module, path):
    """
    Import all submodules and register them in the ``context`` namespace.

    >>> import_submodules(locals(), __name__, __path__)
    """
    for _loader, module_name, _is_pkg in pkgutil.walk_packages(path, root_module + '.'):
        # this causes a Runtime error with model conflicts
        # module = loader.find_module(module_name).load_module(module_name)
        module = __import__(module_name, globals(), locals(), ['__name__'])
        for k, v in six.iteritems(vars(module)):
            if not k.startswith('_'):
                context[k] = v
        context[module_name] = module
