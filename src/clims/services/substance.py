from __future__ import absolute_import

import six
import re
import logging
from datetime import datetime

from clims import utils
from clims.models.substance import Substance, SubstanceVersion
from clims.models.extensible import ExtensibleProperty
from clims.models.location import SubstanceLocation
from clims.models.file import MultiFormatFile
from clims.services.extensible import (ExtensibleBase, HasLocationMixin)
from django.db import transaction
from django.db.models import QuerySet
from uuid import uuid4
from sentry.models.file import File
from clims.models.file import OrganizationFile
from clims.handlers import SubstancesSubmissionHandler
from clims.handlers import SubstancesValidationHandler
from clims.services.base_extensible_service import BaseExtensibleService
from clims.services.base_extensible_service import BaseQueryBuilder
from clims.models.base import ResultIterator
from clims.handlers import context_store

logger = logging.getLogger(__name__)


class NotFound(Exception):
    pass


# TODO: Decide what to do if a plugin does something that requires more rights than the action
# that initiated it (and if that's required)
class ExtensibleBaseQuerySet(QuerySet):
    pass


class FileNameValidationError(Exception):
    pass


FILENAME_RE = re.compile(r"[\n\t\r\f\v\\]")


class SubstanceAncestry(object):
    """
    A companion class to the `Substance` class. Used to visualize the substance's ancestry.
    """

    def __init__(self, substance):
        self.substance = substance

    def items(self):
        # Find out the origin nodes of the graph we are in. Note that substance graphs
        # can have 1..n origin nodes. An example of that is when you create a pool
        # from two original samples. There your pool's origin are the two original samples.

        # Now, to find all the nodes in the graph, we simply query for the origin nodes:
        qs = Substance.objects.filter(origins__in=self.substance.origins)
        return ResultIterator(qs, self.substance._to_wrapper)

    def to_graphviz_src(self, include_created=True):
        """Generates a graphviz graph for the ancestry of this substance."""
        def create_node_id(substance_at_version):
            return "node_{}_v{}".format(substance_at_version.id, substance_at_version.version)

        def node(substance):
            node_id = create_node_id(substance)
            node_name = "{}.v{}".format(substance.name, substance.version)
            key_vals = list((key, prop.value) for key, prop in substance.properties.items())
            # Add created/updated
            if include_created:
                key_vals.append(("created", substance.created_at))

            keys = " | ".join(key for key, val in key_vals)
            vals = " | ".join(six.text_type(val) for key, val in key_vals)

            templ = "{ID} [shape=record,label=\"{{NAME} | {{ " + keys + " } | { " + vals + " }}}\"];"
            templ = templ.replace("{ID}", node_id)
            templ = templ.replace("{NAME}", node_name)
            return templ

        nodes = list()
        edges = list()

        # Create edges for parent/child relationships and versions
        for current in self.items():
            all_versions = {s.version: s for s in current.iter_versions()}
            for current_at_version in all_versions.values():
                nodes.append(node(current_at_version))

                # We show the parent-child relationship only at version 1, because when
                # we build a parent/child relationship, the child is always at version 1
                # by definition (because it's new)
                if current_at_version.version == 1:
                    for parent in current.parents:
                        edges.append("{} -> {}".format(
                            create_node_id(parent), create_node_id(current_at_version)))

            # Create an edge between versions:
            for ix in range(2, len(all_versions) + 1):
                edges.append("{} -> {} [style=dashed]".format(
                    create_node_id(all_versions[ix - 1]), create_node_id(all_versions[ix])))

        templ = ("digraph structs {\n"
                "  node [shape=record];\n"
                "{NODES}\n"
                "{EDGES}\n"
                "}")

        def format_lines(lines, indent):
            lines = [(" " * indent) + line for line in lines]
            return "\n".join(lines)

        nodes = format_lines(nodes, 6)
        edges = format_lines(edges, 6)

        return templ.replace("{NODES}", nodes).replace("{EDGES}", edges)

    def to_svg(self, include_created=True):
        from graphviz import Source
        s = Source(self.to_graphviz_src(include_created))
        return s


class SubstanceBase(HasLocationMixin, ExtensibleBase):
    """
    A base object for defining substances in the system, e.g. Sample, Aliquot or Pool.

    Details:

    Under the hood, this object wraps a Substance object and its related Extensible* classes.
    """

    WrappedArchetype = Substance
    WrappedVersion = SubstanceVersion

    def __init__(self, **kwargs):
        # TODO: Refactor so that super can come first
        self._unsaved_parents = kwargs.pop('parents', None)
        super(SubstanceBase, self).__init__(**kwargs)
        self._new_location = None

    def _to_wrapper(self, model):
        """
        Wraps either a SubstanceVersion or Substance as a higher-level object
        """
        return self._app.substances.to_wrapper(model)

    @property
    def version(self):
        return self._wrapped_version.version

    @property
    def organization(self):
        return self._archetype.organization

    @property
    def extensible_type(self):
        return self._archetype.extensible_type

    @property
    def depth(self):
        return self._archetype.depth

    @property
    def assignments(self):
        return self._archetype.assignments

    @property
    def origins(self):
        return [origin.id for origin in self._archetype.origins.all()]

    @property
    def parents(self):
        """
        Returns the parents (of a particular version) of the substance, if there are any.
        """
        qs = self._archetype.parents.all()
        return ResultIterator(qs, self._app.substances.to_wrapper)

    @property
    def project(self):
        return self._app.projects.to_wrapper(self._archetype.project)

    @project.setter
    def project(self, project):
        self._archetype.project = project._archetype

    @property
    def location(self):
        """
        Returns the location of the substance as a `ContainerIndex` object.
        """
        # TODO: Prefetch the current position
        # TODO: Wrap in a higher level object that makes sense (e.g. PlateIndex, which
        # we might want to rename to PlateLocation at the same time, since it can have a pointer
        # to the container)
        try:
            loc = self._archetype.locations.get(current=True)
        except SubstanceLocation.DoesNotExist:
            return None

        # TODO: the container should be in a local cache!
        # when looping samples in a container, the very same container is fetched over and
        # over again
        container = self._app.containers.to_wrapper(loc.container)
        return container.IndexType.from_internal_coordinates(container, loc.x, loc.y, loc.z)

    def to_ancestry(self):
        return SubstanceAncestry(self)

    def _save_parents(self):
        parents = [substance_base._wrapped_version for substance_base in self._unsaved_parents]
        self._archetype.parents.add(*parents)
        self._archetype.depth = max([p.depth for p in self._unsaved_parents]) + 1

    def _get_origins(self):
        origins = list()
        if self._unsaved_parents:
            for p in self._unsaved_parents:
                for origin in p._archetype.origins.all():
                    origins.append(origin)
        else:
            origins.append(self._archetype)
        return origins

    def _save_custom(self, creating):
        if creating:
            if self._unsaved_parents:
                self._save_parents()

            self._archetype.save()

            # We want the origin point(s) to always be populated, also for the origins themselves, in
            # which case it points to itself. This way we can find all related samples in one query.
            origins = self._get_origins()
            self._archetype.origins.add(*origins)

        self._save_location()

    @transaction.atomic
    def create_child(self, name=None, **kwargs):
        """
        Creates a child from this substance, giving it a name. If name is not supplied it
        will get a unique name based on the name of the parent.

        The child gets all the props that are in the parent, except if they are in kwargs, then
        kwargs overrides it. If the props are in kwargs but not in the parent, they should be set.
        """

        overridden_properties = kwargs
        parent_version = self._archetype.versions.get(latest=True)

        if not name:
            name = "{}:{}".format(self.name, uuid4())

        child = Substance(
            name=name,
            organization=self.organization,
            extensible_type=self.extensible_type)
        child.depth = self.depth + 1
        child.save()
        version = SubstanceVersion(archetype=child)
        version.save()

        # Origin points to the first ancestor(s) of this substance. If the substance being cloned
        # has origins, we'll get the same origins. Otherwise the substance being
        # cloned is the origin - in that case, it points to itself.

        for origin in self._archetype.origins.all():
            child.origins.add(origin)

        child.parents.add(parent_version)

        for prop in parent_version.properties.all():
            if prop.name in overridden_properties:
                overridden_val = overridden_properties.pop(prop.name, None)
                if overridden_val == prop.value:
                    # Link to the existing property
                    version.properties.add(prop)
                elif overridden_val is None:
                    # Providing an override with value None means we don't add the prop to the child
                    pass
                else:
                    prop = ExtensibleProperty(extensible_property_type=prop.extensible_property_type)
                    prop.value = overridden_val
                    prop.save()
                    version.properties.add(prop)
            else:
                # Link to the existing property
                version.properties.add(prop)

        for key, val in overridden_properties.items():
            prop_type = child.extensible_type.property_types.get(name=key)
            prop = ExtensibleProperty(extensible_property_type=prop_type)
            prop.value = val
            prop.save()
            version.properties.add(prop)

        return self._app.substances.to_wrapper(child)


class SubstanceService(BaseExtensibleService):
    """
    Provides an API for dealing with both substances (samples, aliquots etc.)
    and their associated containers.

    Plugins change the state of the system only via service classes or REST API
    calls. Access to lower-level APIs is possible, but not suggested to ensure
    backwards compatibility and business rule constraints.

    NOTE: Use this class instead of the manager on Substance even in framework code (unless
    you're sure of what you're doing) because interaction of the substance and its properties must
    be strictly maintained.
    """

    def __init__(self, app):
        super(SubstanceService, self).__init__(app, SubstanceBase)

    def get_submission_files(self, context):
        # TODO: Currently returns OrganizationFile. Need to filter it down to only substance files
        #       So add a "type" to the file.
        return OrganizationFile.objects.filter(organization=context.organization)

    def get_submission_file(self, file_id):
        try:
            return OrganizationFile.objects.get(id=file_id)
        except OrganizationFile.DoesNotExist:
            raise NotFound("Can't find file with id '{}'".format(file_id))

    @transaction.atomic
    def load_file(self, full_path, file_stream, add_timestamp=False):
        """
        Loads the file into the system.

        On a successful run, returns a tuple of the loaded file and any non-error validation issues
        that may have occurred while processing.
        """

        logger.info("Loading file {}".format(full_path))

        non_error_validation_issues = list()

        # TODO: Decide what we want to happen here. Should the user be able to load files
        # with an identical name or not? Makes more sense to me that we inspect if samples
        # with the same name have been uploaded or not. So for now we add this timestamp to the name

        # Add a timestamp (so files can be uploaded that have the same name)
        if add_timestamp:
            full_path, ext = full_path.rsplit(".", 1)
            full_path = full_path + datetime.now().strftime("%m_%d_%Y%_H_%M_%S") + "." + ext

        with MultiFormatFile.from_file_stream(full_path, file_stream) as wrapped_stream:
            handlers = self._app.plugins.handlers.handle(
                SubstancesValidationHandler, context_store.current, required=False,
                multi_format_file=wrapped_stream)

            # Since we're here, there were no exceptions during the run of the handler(s), but
            # there might be other validation issues:
            for handler in handlers:
                non_error_validation_issues.extend(handler.validation_issues)

        logger.info('substance_batch_import.start')

        org_file = self._create_organization_file(file_stream, full_path,
                context_store.current.organization.id)

        with MultiFormatFile.from_organization_file(org_file) as wrapped_org_file:
            self._app.plugins.handlers.handle(
                SubstancesSubmissionHandler, context_store.current, required=True,
                multi_format_file=wrapped_org_file)

        return org_file, non_error_validation_issues

    def _create_organization_file(self, file_stream, full_path, organization_id):
        """
        Uploads file to the server and wrap it in a organization file
        """
        name = full_path.rsplit('/', 1)[-1]
        if FILENAME_RE.search(name):
            raise FileNameValidationError('File name must not contain special whitespace characters')

        file_model = File.objects.create(
            name=name,
            type='substance-batch-file',
            headers=list(),
        )

        file_stream.seek(0)
        file_model.putfile(file_stream, logger=logger)

        org_file = OrganizationFile.objects.create(
            organization_id=organization_id,
            file=file_model,
            name=full_path,
        )
        return org_file

    def create_submission_demo(self, file_type):
        """
        Returns a demo submission file-like object
        """
        import os
        from clims.handlers import SubstancesSubmissionFileDemoHandler
        self._app.plugins.handlers.require_single_handler(SubstancesSubmissionFileDemoHandler)
        handlers = self._app.plugins.handlers.handle(SubstancesSubmissionFileDemoHandler, None, True, file_type)
        handler = utils.single(handlers)
        handler.demo_file.seek(0, os.SEEK_END)
        size = handler.demo_file.tell()
        handler.demo_file.seek(0)
        logger.debug("Created a sample submission demo file '{}', size={}".format(handler.demo_file_name, size))
        return handler.demo_file, handler.demo_file_name, size

    def filter_by_project(self, project_name):
        # TODO: add organization to the filter parameters
        return self.filter(project_name=project_name)

    def get_by_name(self, name):
        # TODO: add organization to the filter parameters
        return self.get(name=name)

    @classmethod
    def _filter_by_extensible_version(cls, query_set):
        return query_set.filter(substanceversion__latest=True)


class SubstanceQueryBuilder(BaseQueryBuilder):
    def parse_params_for_class(self, key, val):
        query_params = {}
        # TODO: these fields shouldn't be hard coded
        if key == "sample.name":
            query_params['name__icontains'] = val
        elif key == "substance.color":
            query_params['properties__extensible_property_type__name'] = 'color'
            query_params['properties__string_value'] = val
        elif key == 'substance.sample_type':
            query_params['properties__extensible_property_type__name'] = 'sample_type'
            query_params['properties__string_value'] = val
        elif key == "substance.container":
            query_params['archetype__locations__current'] = True
            query_params['archetype__locations__container__name'] = val
        else:
            raise NotImplementedError("The key {} is not implemented".format(key))
        return query_params
