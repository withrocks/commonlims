from __future__ import absolute_import

import logging
import six
from clims import utils
from clims.models import Workflow
from django.db import transaction
from clims.services.extensible import ExternalExtensibleBase
from clims.services.substance import SubstanceBase
from clims.services.container import ContainerBase
from clims.db import assert_no_transaction
from sentry.db.models import sane_repr
from itertools import product
from collections import defaultdict

logger = logging.getLogger(__name__)


class WorkflowBase(ExternalExtensibleBase):
    """Base class for defining a workflow in a plugin"""

    unique_registration = False
    require_name = False
    assign_substances_rather_than_containers = True

    # Override this to add tasks from this workflow that should register for available work.
    # These will show up in the available work view and can be used to form a WorkBatch
    available_work = []

    def __init__(self, **kwargs):
        super(WorkflowBase, self).__init__(**kwargs)
        self._presets = dict()

    # TODO: Currently using both the class and the object when registering etc, that's why
    # there are two name "fields". Consider using only instances of the WorkflowBase, as that's
    # required for the presets in any case.
    @classmethod
    def get_full_name(cls):
        return utils.class_full_name(cls)

    @property
    def id(self):
        return self.get_full_name()

    def assign_item(self, item):
        """
        Assigns a single "business item" to the workflow.
        """
        self._context.app.workflows.assign_item(self, item, self._context.user)

    def assign_container(self, container):
        if self.assign_substances_rather_than_containers:
            for item in container.contents:
                if isinstance(item, SubstanceBase):
                    self.assign_item(item)
        else:
            self.assign_item(container)

    @property
    def variables(self):
        """The workflow (also called process) variables, which are sent to the workflow engine"""
        return self._property_bag.store

    def assign(self, *items):
        """
        Assigns a list of substances or containers to a workflow.

        If the item is a container, each of the substances in it are assigned if the
        flag assign_items_in_containers is set to True. This allows a plugin developer
        to define Workflows that expect containers rather than substances, while they can
        also use the default, where each item in the container is assigned to the workflow.
        """

        for item in items:
            if isinstance(item, SubstanceBase):
                self.assign_item(item)
            elif isinstance(item, ContainerBase):
                self.assign_container(item)
            else:
                raise AssertionError(
                    "Can only assign a container or a substance")

    def preset(self, name, **kwargs):
        """
        Creates a preset with the name and kwargs and then adds it to the workflows presets

        Presets allow the plugin developer to define a named set of variables for a workflow process
        This can make it easier for users to start processes that have a complex set of variables.
        They can either be defined with a dictionary on the class like this

        presets = {
           'NovaSeq Ready-made libraries': {
               sample_prep: 'Ready-made libraries',
               sequencer: 'NovaSeq',
               sample_type: 'Unknown',
        }

        or, for flexibility, they can be defined as a method instead, which may make
        complex presets easy to define. E.g.:

        def presets(self):
            self.preset('{sequencer}: {sample_type} prepared with {sample_prep}',
                        sample_prep=['pa', 'pb'],
                        sample_type=['sa', 'sb'],
                        sequencer=['Android'])
        """
        new_preset = create_preset(name, **kwargs)
        self._presets.update(new_preset)

    def get_presets(self):
        """
        Fetches the presets defined in a subclass either with a dictionary called `presets`
        if it exists, or, if that doesn't exist, the private `_presets` dictionary which
        the user may have added to.
        """

        if hasattr(self, "presets"):
            if callable(self.presets):
                # The subclass defines presets as a function. Call it and it is expected to update
                # the private variable _presets:
                self.presets()
                return self._presets
            else:
                # The subclass has defined presets as a dict:
                return self.presets

        # No definitions found
        return dict()


def create_preset(name, **kwargs):
    """
    Adds a preset by name having the variables set with kwargs.

    The name can be a template string that refers to one of the variables in kwargs.

    If any of the kwarg is an iterable (and not a string) values will be generated for every
    value in that iterable. If there are more than one iterable, the product of them is used.

    Example:

    >>> create_preset("{sequencer} {method}", sequencer=["A", "B"], method=["m1", "m2"], sample_type="DNA")
    {
      'A m1': {'method': 'm1', 'sequencer': 'A', 'sample_type': 'DNA'},
      'A m2': {'method': 'm2', 'sequencer': 'A', 'sample_type': 'DNA'},
      'B m1': {'method': 'm1', 'sequencer': 'B', 'sample_type': 'DNA'},
      'B m2': {'method': 'm2', 'sequencer': 'B', 'sample_type': 'DNA'}
    }
    """

    # TODO: Do doctests support dictinoaries like above?
    try:
        from collections.abc import Iterable
    except ImportError:
        from collections import Iterable

    iterables = []
    non_iterables = []
    ret = dict()

    for key, val in kwargs.items():
        if isinstance(val, Iterable) and not isinstance(val, six.string_types):
            iterables.append([(key, x) for x in val])
        else:
            non_iterables.append((key, val))

    for x in product(*iterables):
        variables = dict(list(x) + non_iterables)

        try:
            formatted_name = name.format(**variables)

            if formatted_name in ret:
                raise SameNameDefinedMoreThanOnce(
                    "Trying to use the preset name '{}' more than once "
                    "this is not allowed".format(formatted_name))
            ret[formatted_name] = variables
        except KeyError as e:
            raise FormatError(
                "Not able to interpolate {} into '{}'. Make sure that the name of the "
                "preset refers to one of the variable names specified: {}".
                format(six.text_type(e), name, kwargs.keys()))
    return ret


class FormatError(Exception):
    pass


class SameNameDefinedMoreThanOnce(Exception):
    pass


class AssignmentError(Exception):
    pass


class WorkflowService(object):
    AssignmentError = AssignmentError

    def __init__(self, app):

        self._app = app

        from .camunda import CamundaWorkflow
        from .camunda.client import CamundaClient

        # A dict of handlers that proxy an external workflow management system:
        self.handlers = {
            "camunda": {
                "key": "camunda",
                "cls": CamundaWorkflow,
                "handler": CamundaClient(self._app.settings.CAMUNDA_API_URL)
            }
        }

    def install(self, workflow_cls, plugin_reg):
        """
        Installs a workflow definition
        """
        # TODO: We should validate that the workflow has the same Id as the class' full name, or
        # even change the XML before it goes in so it always has the same(?) If they don't
        # match, the user won't be able to assign to it.
        # definition_path = workflow_cls.get_bpmn_path()
        handler = self.get_handler(workflow_cls)

        logger.debug("Installing workflow {} with handler {}".format(
            workflow_cls, handler))
        installed = handler.install_from_workflow_class(workflow_cls)

        logger.debug("Workflow definition from Camunda: {}".format(
            repr(installed)))

        # Fetch the latest matching workflow definition in Camunda and make sure they match:
        # Either there should be an entry that is of the previous version, meaning that we just
        # added this definition for the first time, or our 'latest' is the same version, meaning
        # that we have already installed this version. Anything else is an error

        # TODO: create index based on query
        name = utils.class_full_name(workflow_cls)
        latest_db_entry = Workflow.objects.filter(name=name, latest=True)
        latest_db_entry = utils.single_or_default(latest_db_entry)
        db_version = latest_db_entry.version if latest_db_entry else 0

        if installed.version == db_version:
            logger.debug(
                "The workflow definition has already been installed in the DB")
        elif installed.version - db_version == 1:
            # Note that the `installed` object is a partially complete django model already:
            installed.plugin_registration = plugin_reg
            logger.debug(
                "Installed version {} in Camunda, DB version is {}".format(
                    installed.version, db_version))
            with transaction.atomic():
                # Update the latest flag on the previous entry:
                if latest_db_entry:
                    latest_db_entry.latest = False
                    latest_db_entry.save()
                installed.latest = True
                installed.save()
        else:
            raise AssertionError(
                "Workflow definition in Camunda ({}) and DB ({}) unexpectedly not sequential"
                .format(installed.version, db_version))

    @transaction.atomic
    def create_work_batch(self, task_ids, organization):
        """
        Creates a new WorkBatch for a list of tasks
        """

        # 1. Fetch all the tasks from the task IDs we received
        tasks = self.get_tasks_by_ids(task_ids)
        name = list({t.name for t in tasks})
        if len(name) > 1:
            raise AssertionError("Expecting only one task name when creating a work batch, got: '{}'".format(name))
        name = name[0]

        # 2. Create a work batch with the "tracked objects" we just fetched
        from clims.models.work_batch import WorkBatch
        batch = WorkBatch(organization=organization, name=name)
        batch.save()

        for task in tasks:
            task.tracked_object._archetype.work_batches.add(batch)
            task.tracked_object._archetype.save()

        # TODO(clims-345): Make sure that we're not adding a substance to another workbatch if
        # it's already "locked".
        return batch

    def get_tasks_by_ids(self, task_ids):
        task_ids_by_provider = defaultdict(list)

        for task_id in task_ids:
            provider_id, id = task_id.split("/")
            task_ids_by_provider[provider_id].append(id)

        tasks = list()
        for provider_id, ids in task_ids_by_provider.items():
            handler = self.handlers[provider_id]["handler"]
            tasks.extend(handler.get_tasks_by_ids(ids))
        self._materialize_tracked_objects(tasks)
        return tasks

    def get_handler(self, workflow_cls):
        for handler_config in self.handlers.values():
            configured_class = handler_config["cls"]
            if issubclass(workflow_cls, configured_class):
                return handler_config["handler"]
            else:
                raise NotImplementedError(
                    "Workflow class '{}' has no handler".format(workflow_cls))

    def AssignmentModel(self, item, user):
        # Creates an "assignment" model based on which item we're assigning to a workflow
        # This model is a historical record in the database about which assignment was made,
        # by whom, when etc.
        from clims.services.substance import SubstanceBase
        from clims.models import SubstanceAssignment

        # The DB model we'll hook up to:
        model = item._archetype

        if not model.id:
            raise AssignmentError(
                "Can't create an assignment model for unsaved model: {}".
                format(model))

        if isinstance(item, SubstanceBase):
            return SubstanceAssignment(substance=model, user=user)
        else:
            raise AssignmentError("Unexpected item {}".format(item))

    def assign_item(self, workflow, item, user):
        from clims.models import SubstanceAssignment

        # Fetch the handler that takes care of creating the workflow in the external workflow engine
        handler = self.get_handler(workflow.__class__)
        assignment = self.AssignmentModel(item, user)

        # Fetch the model we use to keep a history of the item

        # NOTE: We don't want the assignment to be saved in a transaction. The reason is that
        # we want an uncompleted item in the assignment table to be able to identify workflows
        # we might have started or not, of which we don't have any record. This is necessary
        # since the workflow engine is outside of our database transactions.
        assert_no_transaction()
        assignment.status = SubstanceAssignment.STATUS_REQUESTING
        assignment.save()

        # Start the workflow in the external system:
        handler.start_workflow(workflow, item)

        assignment.status = SubstanceAssignment.STATUS_DELIVERED
        assignment.save()

    def move_substance(self):
        raise NotImplementedError()

    # TODO: Naming
    def batch_get_tracked_objects(self, category, keys):
        """
        Fetches the tracked object based on the category key, e.g. `Substance` or `Container`
        """
        if category == "Substance":
            from clims.models import Substance
            return [(self._app.substances.to_wrapper(x))
                    for x in Substance.objects.filter(id__in=keys)]
        elif category == "Container":
            from clims.models import Container
            return [(self._app.containers.to_wrapper(x))
                    for x in Container.objects.filter(id__in=keys)]
        else:
            raise AssertionError(
                "Object of category {} is not supported".format(category))

    def _materialize_tracked_objects(self, tasks):
        """Materializes the tracked objects in the tasks"""
        tasks_grouped_by_category = defaultdict(list)
        tasks_grouped_by_global_id = defaultdict(list)
        for task in tasks:
            tasks_grouped_by_category[task.tracked_object_category].append(
                task)
            tasks_grouped_by_global_id[task.tracked_object_global_id].append(
                task)

        # We fetch all objects for a certain category in a batch
        for category, tasks in tasks_grouped_by_category.items():
            keys = [task.tracked_object_local_id for task in tasks]
            tracked_objects = self.batch_get_tracked_objects(category, keys)

            for tracked_object in tracked_objects:
                for task in tasks_grouped_by_global_id[
                        tracked_object.global_id]:
                    task.tracked_object = tracked_object
        return tasks

    def get_tasks(self, task_definition_key=None, process_definition_key=None):
        # TODO: If we ever have more than one workflow engine, fetching asynchronously would make
        # a lot of sense here
        # TODO: Handle paging, sorting and so on.
        all_tasks = list()

        for handler_config in self.handlers.values():
            handler = handler_config["handler"]
            tasks_in_handler = handler.get_tasks(task_definition_key,
                                                 process_definition_key)
            all_tasks.extend(tasks_in_handler)

        # The clients return only the global_id of the tracked objects. We must fetch the objects here
        # for the caller:
        self._materialize_tracked_objects(all_tasks)

        return all_tasks

    def batch_assign_items(self, category, items):
        """
        Assigns a batch of items by global_id.

        If the global_id represents more than one category (e.g. Substance_1 and Container_2),
        they will be split in two batches
        """
        raise NotImplementedError()

    def get_process_definitions(self):
        # TODO: During the load phase, we should create instances of these classes
        # and keep them in an instance manager (can be lazy loaded though)
        for plugin in self._app.plugins.all():
            for definition in plugin.get_process_definitions():
                yield definition()

    def _get_workflow_process_by_name(self, process_name):
        # TODO-simple: memoize?
        for definition in self.get_process_definitions():
            if definition.get_full_name() == process_name:
                # TODO: Ugly. Doing this because currently get_workflows returns objects rather than classes
                return definition.__class__
        raise WorkflowProcessNotFound(process_name)

    def batch_assign(self, entities, process, user, variables):
        """
        Assigns all entities in the list. The entities must use global id (e.g. Substance-1)

        :process: either be either a name and namespace of a process, e.g.
                  clims.plugins.demo.dnaseq.workflows.sequence.SequenceSimple or an instance of
                  WorkflowBase

        :returns: Number of substances assigned to the process
        """
        from clims.models import SubstanceAssignment

        logger.debug("Assigning entities '{}' to process '{}'".format(
            entities, process))

        if isinstance(process, six.string_types):
            Process = self._get_workflow_process_by_name(process)
            process = Process()
            for key, val in variables.items():
                setattr(process, key, val)

        # Fetch the handler that takes care of creating the workflow in the external workflow engine
        handler = self.get_handler(process.__class__)

        assert_no_transaction()
        assignments = list()

        # TODO: Only supporting substances for now:
        entities = [int(global_id.split("-")[1]) for global_id in entities]

        # TODO-auth: Here we should make sure that all these substances are in the user's org
        substances = self.batch_get_tracked_objects("Substance", entities)

        # Mark all as starting to assign:
        with transaction.atomic():
            for substance in substances:
                assignment = self.AssignmentModel(substance, user)
                assignment.status = SubstanceAssignment.STATUS_REQUESTING
                assignment.save()
                assignments.append(assignment)

        # Start the workflow in the external system. If unsuccessful, we'll have entries
        # in the SubstanceAssignment table that are still in STATUS_REQUESTING, indicating
        # something went wrong (but not exactly what).

        handler.start_workflows(process, substances)

        with transaction.atomic():
            for assignment in assignments:
                assignment.status = SubstanceAssignment.STATUS_DELIVERED
                assignment.save()

        return assignments

    def batch_assign_containers(self, containers, process, user, variables):
        """
        Assigns all containers in the list. If an entry is an integer, it's assumed to be
        an id of a container. Otherwise it must inherit from ContainerBase.
        """
        # TODO
        raise NotImplementedError()

    def get_task_definitions(self, process_definition_key=None, task_definition_key=None):
        from clims.models import CamundaTask
        from django.db.models import Count
        from django.db.models import Q

        # TODO: Only supports camunda
        task_definitions = CamundaTask.objects.select_related('process_definition')

        # Temporary: Remove Camunda demo data results:
        task_definitions = task_definitions.filter(~Q(process_definition__key='invoice'))

        if process_definition_key:
            task_definitions = task_definitions.filter(process_definition__key=process_definition_key)
        if task_definition_key:
            task_definitions = task_definitions.filter(task_definition_key=task_definition_key)

        task_definitions_with_instance_count = task_definitions.values(
            'task_definition_key', 'name', 'process_definition__name',
            'process_definition__key').annotate(count=Count('name'))

        ret = list()
        for entry in task_definitions_with_instance_count:
            entry["id"] = "{}/{}".format(
                entry["process_definition__key"], entry["task_definition_key"])
            ret.append(
                TaskDefinitionInfo(entry["id"], entry["name"], entry["process_definition__key"],
                        entry["task_definition_key"],
                    entry["process_definition__name"], entry["count"]))
        return ret


class TaskDefinitionInfo(object):
    def __init__(self, id, name, process_definition_key, task_definition_key, process_definition_name, count):
        self.id = id
        self.name = name
        self.process_definition_key = process_definition_key
        self.process_definition_name = process_definition_name
        self.task_definition_key = task_definition_key
        self.count = count


class ProcessTask(object):
    """Represents a single instance of a step running in a workflow process."""

    def __init__(self, id, process_instance_id, provider_type,
                 tracked_object_global_id, name):
        # TODO-simple: Also use a slash for global ids of e.g. substances
        self.id = "{}/{}".format(provider_type, id)
        self.process_instance_id = process_instance_id

        # The ID of the "tracked object" in the external. This is (for now) either
        # Substance_<internal_id> or Container_<internal_id>
        self.tracked_object_global_id = tracked_object_global_id
        self.tracked_object = None
        self.name = name

    @property
    def tracked_object_category(self):
        category, _ = self.tracked_object_global_id.split("-")
        return category

    @property
    def tracked_object_local_id(self):
        _, id = self.tracked_object_global_id.split("-")
        return id

    __repr__ = sane_repr('process_instance_id', 'tracked_object_global_id')


class WorkflowProcessNotFound(Exception):
    pass
