"""
sentry.plugins.base.manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2013 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from __future__ import absolute_import, print_function

__all__ = ('PluginManager', )

import sys
import os
import six
import logging
import click
import importlib

from clims.handlers import HandlerManager
from sentry.utils.managers import InstanceManager
from sentry.utils.safe import safe_execute
from django.conf import settings
from django.db import transaction
from django.db.utils import ProgrammingError

logger = logging.getLogger(__name__)


class PluginManager(object):
    """
    Handles plugins.

    Plugins need to be installed via a call to `lims upgrade`. This will install all plugins
    that are found in the application at the time.

    When a plugin is found in the environment, it's installed, i.e. added to the database.
    After that, it needs to exist on load time from there on. It's currently not supported to
    uninstall a plugin.

    When the application loads, it will load all plugins that exist in the database.
    """

    def __init__(self, app, instance_manager=None):
        self._app = app
        self.handlers = HandlerManager(app)
        self.instance_manager = instance_manager or InstanceManager()

    # Install (during upgrade)

    def auto_install(self):
        """
        Installs all plugins that can be found in the Python environment. An entry for the plugin
        and version is created in the database.
        """
        logger.info("Auto installing plugins found in environment")
        plugins = self.find_all_plugins_in_scope()
        self.install_plugins(*plugins)

    def install_plugins(self, *plugins):
        """
        Installs the plugins in the backend. Plugins can not be loaded before they have been
        installed.
        """
        for plugin in plugins:
            logger.info("Installing plugin class '{}'".format(plugin.get_name_and_version()))
            with transaction.atomic():
                plugin_reg = self.install_plugin(plugin)
                self.install_extensible_types(plugin)
                self.install_workflows_in_plugin(plugin, plugin_reg)

    def install_workflows_in_plugin(self, plugin_cls, plugin_reg):
        """
        Installs workflow definitions found in the plugin.
        """

        logger.info("Loading workflows for plugin class {}".format(plugin_cls))

        definitions = list(plugin_cls.get_process_definitions())

        logger.info("Found {} workflow definitions for plugin class {}".format(
            len(definitions), plugin_cls))

        for definition in definitions:
            self._app.workflows.install(definition, plugin_reg)

    def validate_version(self, plugin_cls):
        if not plugin_cls.version:
            raise PluginMustHaveVersion()

        # Ensure that we can parse the string as a sortable tuple:
        try:
            parsed = plugin_cls.get_sortable_version()
            logger.debug("Plugin {} has a valid version {} => {}".format(
                plugin_cls, plugin_cls.version, parsed))
        except ValueError:
            raise PluginIncorrectVersionFormat(
                "Plugin versions must be a list of dot separated numbers, e.g. 1.0.0")

    def install_plugin(self, plugin_cls):
        """
        Installs the plugin in the database.

        This method should be called when upgrading the system, so the end-user is in control
        of when a new model is available.

        Returns a plugin registration model that represents the installation.
        """
        # Make sure we have a plugin registration here:
        from clims.models import PluginRegistration

        self.validate_version(plugin_cls)

        logger.debug("Recording plugin {} version={} in the database".format(
            plugin_cls.get_full_name(), plugin_cls.version))

        reg, _ = PluginRegistration.objects.get_or_create(
            name=plugin_cls.get_full_name(), version=plugin_cls.version)
        return reg

    def install_extensible_types(self, plugin):
        """
        Installs all the extensible types found in the plugin. These are for example specific
        Plates, Projects and Samples defined by the plugin developers.
        """
        logger.info("Installing extensible types found in plugin class '{}'".format(
            plugin.get_name_and_version()))
        from clims.models import PluginRegistration

        plugin_model = PluginRegistration.objects.get(name=plugin.get_full_name(),
                version=plugin.version)

        for extensible_cls in plugin.get_extensible_objects():
            self._app.extensibles.register(plugin_model, extensible_cls)

    def get_extensible_types_from_db(self):
        """
        :return: class objects of extensible types
        """
        from clims.models.extensible import ExtensibleType

        extensible_types = ExtensibleType.objects.all()
        type_names_in_db = [e.name for e in extensible_types]
        for type_name in type_names_in_db:
            split_type_name = type_name.split('.')
            full_module_name = '.'.join(split_type_name[:-1])
            extensible_class_name = split_type_name[-1]
            module = self._import_module(full_module_name)
            extensible_class = getattr(module, extensible_class_name, None)
            yield extensible_class

    def find_plugins_by_entry_points(self):
        """
        Returns plugins that have been marked as such by adding an entry like:

            entry_points={
                'clims.plugins': [
                    'org_plugins = org_plugins.plugins:YourPlugin',
                ],
            },

        to the setup.py file in the plugin package.
        """

        # NOTE: Users must specify an entry_point in their setup.py so that plugins will
        # be discovered.
        # See e.g.: https://github.com/Molmed/commonlims-snpseq/blob/cd1c011a3/setup.py#L105
        from pkg_resources import iter_entry_points
        entry_points = [ep for ep in iter_entry_points('clims.plugins')]

        for ep in entry_points:
            try:
                plugin = ep.load()
                yield plugin
            except Exception:  # Handling all exceptions since the code is unknown to us.
                import traceback
                click.echo(
                    "Failed to load plugin %r:\n%s" % (ep.name, traceback.format_exc()),
                    err=True)

    def find_all_plugins_in_scope(self):
        """
        Yields all plugins that should be used, based on what can be found in the python environment.
        """
        for plugin in self.find_plugins_by_entry_points():
            yield plugin

    # Load (runtime)

    def load_installed(self):
        """
        Loads all plugins that have been installed.

        Takes the latest PluginRegistration found for each plugin and loads it. If the plugin
        isn't installed anymore, or has a different version, an error is raised.
        """
        logger.info("Loading all installed plugins")
        from clims.models import PluginRegistration
        try:
            installed = list(PluginRegistration.objects.all())
        except ProgrammingError:
            # We might be loading the application before migrations have run, so the
            # PluginRegistration type doesn't exist. In this case we silently pass and no plugins
            # will be loaded
            return

        latest = dict()
        for current in installed:
            if current.name in latest \
                    and latest[current.name].sortable_version > current.sortable_version:
                logger.debug("Found registration for {} but newer already found".format(current.name_and_version))
                continue
            logger.debug("Found a registration for {}".format(current.name_and_version))
            latest[current.name] = current

        for plugin_registration in latest.values():
            self.load(plugin_registration)

        self.handlers.validate()
        logger.info("Active handlers after loading and validating all plugins:\n{}".format(
            self.handlers.to_handler_config()))

    def load(self, plugin_registration):
        """
        Initializes the plugin class if it's found. It must match the name and version of the
        PluginRegistration.
        """

        # NOTE: We currently require plugins to load (the True flag). This is because plugins
        # define types that must exist after they've been created. It might be worthy to find
        # a way to deal with plugins that should not load anymore.
        logger.info("Loading plugin '{}@{}'".format(
            plugin_registration.name, plugin_registration.version))

        try:
            plugin = self.instance_manager.add(
                plugin_registration.name, plugin_registration.version, True)
        except self.instance_manager.ImportException:
            # NOTE: We need to find a smooth way of getting rid of the plugin but still have
            # an acceptably functioning system. For now however, this error is raised

            # Allow the user to ignore the plugin if an environment variable is set. This
            # is mainly for debug purposes and to be able to run `lims shell` in this situation.
            if not os.environ.get("CLIMS_IGNORE_UNAVAILABLE_PLUGINS", None) == "1":
                ex_type, ex_value, ex_tb = sys.exc_info()

                six.reraise(RequiredPluginCannotLoad,
                    "Can't import required plugin {}@{}. The plugin has been installed e.g. via "
                    "`lims upgrade` but the implementation is not found in the python environment. "
                    "To override this check, you can set the "
                    "environment variable CLIMS_IGNORE_UNAVAILABLE_PLUGINS=1\n\t{}".format(
                        plugin_registration.name, plugin_registration.version, ex_value), ex_tb)
        except self.instance_manager.InitializeException:
            six.reraise(RequiredPluginCannotLoad,
                    "Can't initialize the plugin {}@{}. The stacktrace has more information on "
                    "why the plugin can not load.".format(
                        plugin_registration.name, plugin_registration.version))

        # Registers handlers. Handlers must be in a module directly below
        # the plugin's module:
        mod = self.get_plugin_module(plugin, 'handlers')
        if not mod:
            logger.info("No handlers module found in plugin '{}'".format(plugin))
        else:
            logger.info("Loading all handlers in plugin '{}'".format(plugin.get_name_and_version()))
            self.handlers.load_handlers(mod)

    def init_plugin_instance(plugin):
        # TODO: Call this when the plugin is run on load time (review requirements first)
        from sentry.plugins import bindings
        plugin.setup(bindings)

        # Register contexts from plugins if necessary
        if hasattr(plugin, 'get_custom_contexts'):
            from sentry.interfaces.contexts import contexttype
            for cls in plugin.get_custom_contexts() or ():
                contexttype(cls)

        if (hasattr(plugin, 'get_cron_schedule') and plugin.is_enabled()):
            schedules = plugin.get_cron_schedule()
            if schedules:
                settings.CELERYBEAT_SCHEDULE.update(schedules)

        if (hasattr(plugin, 'get_worker_imports') and plugin.is_enabled()):
            imports = plugin.get_worker_imports()
            if imports:
                settings.CELERY_IMPORTS += tuple(imports)

        if (hasattr(plugin, 'get_worker_queues') and plugin.is_enabled()):
            from kombu import Queue
            for queue in plugin.get_worker_queues():
                try:
                    name, routing_key = queue
                except ValueError:
                    name = routing_key = queue
                q = Queue(name, routing_key=routing_key)
                q.durable = False
                settings.CELERY_QUEUES.append(q)

    # Query

    def __iter__(self):
        return iter(self.all())

    def __len__(self):
        return sum(1 for i in self.all())

    def all(self, version=None, enabled=None):
        """
        :param version: The version of the plugin interface. None will return all enabled plugins.
        :param enabled: Specifies if only enabled plugins should be returned (True). If None, both
        enabled and disbabled plugins are returned
        :return: A generator that iterates over the plugins
        """
        for plugin in sorted(self.instance_manager.all(), key=lambda x: x.get_title()):
            if enabled is not None and not plugin.is_enabled():
                continue
            if version is not None and plugin.__version__ != version:
                continue
            yield plugin

    def exists(self, slug):
        for plugin in self.all(version=None):
            if plugin.slug == slug:
                return True
        return False

    def get(self, slug):
        for plugin in self.all(version=None):
            if plugin.slug == slug:
                return plugin
        raise KeyError(slug)

    # Legacy

    # These methods are pending deletion (from the sentry core)

    def configurable_for_project(self, project, version=1):
        for plugin in self.all(version=version):
            if not safe_execute(plugin.can_configure_for_project,
                                project, _with_transaction=False):
                continue
            yield plugin

    def for_project(self, project, version=1):
        for plugin in self.all(version=version):
            if not safe_execute(plugin.is_enabled, project, _with_transaction=False):
                continue
            yield plugin

    def for_site(self, version=1):
        for plugin in self.all(version=version):
            if not plugin.has_site_conf():
                continue
            yield plugin

    def get_registered_base_handler(self, cls):
        """
        Returns True if cls is an implementation of a registered handler type
        """
        for handler_type in self.handlers:
            if issubclass(cls, handler_type):
                return handler_type
        return None

    def get_plugin_module(self, plugin_class, name):
        """
        Gets a module defined in the plugin. Returns None if it wasn't found
        """
        full_module_name = '{}.{}'.format(plugin_class.__module__, name)
        return self._import_module(full_module_name)

    def _import_module(self, full_module_name):
        split_name = full_module_name.split('.')
        name = split_name[-1]
        try:
            return importlib.import_module(full_module_name)
        except ImportError as ex:
            if six.text_type(ex) != "No module named {}".format(name):
                trace = sys.exc_info()[2]
                raise ImportError("Error while trying to load plugin {}".format(full_module_name)), None, trace
            logger.debug("Can't find module {}".format(full_module_name))
            return None

    def clear_handler_implementations(self, baseclass=None):
        if baseclass is not None:
            self.handlers[baseclass].clear()
        else:
            for key in self.handlers:
                self.handlers[key].clear()

    def unregister(self, cls):
        self.remove('%s.%s' % (cls.__module__, cls.__name__))
        return cls


class PluginMustHaveVersion(Exception):
    pass


class PluginIncorrectVersionFormat(Exception):
    pass


class RequiredPluginCannotLoad(Exception):
    pass
