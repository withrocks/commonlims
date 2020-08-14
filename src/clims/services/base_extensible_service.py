from __future__ import absolute_import

import six
from abc import abstractmethod
import logging
from django.db.models import Prefetch
from django.core import exceptions as django_exceptions
from clims.services.exceptions import DoesNotExist
from clims.models.extensible import ExtensibleProperty
from clims.models import ResultIterator


class BaseExtensibleService(object):
    """
    A base class for service classes that handle extensible objects.
    """

    DoesNotExist = DoesNotExist

    def __init__(self, app, wrapper_class):
        self._app = app
        self._logger = logging.getLogger(self.__class__.__name__)

        self._wrapper_class = wrapper_class
        self._archetype_class = wrapper_class.WrappedArchetype
        self._archetype_version_class = wrapper_class.WrappedVersion

    def to_wrapper(self, model):
        """
        Wraps the ORM model to a higher level extensible class.
        """
        if model is None:
            return None
        if isinstance(model, self._archetype_version_class):
            return self._version_to_wrapper(model)
        elif isinstance(model, self._archetype_class):
            return self._archetype_to_wrapper(model)
        else:
            raise AssertionError("The model {} can't be wrapped".format(type(model)))

    def _version_to_wrapper(self, version):
        """
        Wraps the ORM model for a particular version to a higher level extensible class.
        """
        name = version.archetype.extensible_type.name
        SpecificExtensibleType = self._app.extensibles.get_implementation(name)
        return SpecificExtensibleType(_wrapped_version=version, _app=self._app)

    def _archetype_to_wrapper(self, archetype):
        versioned = archetype.versions.get(latest=True)
        return self._version_to_wrapper(versioned)

    def all(self):
        """
        Returns all instances of an extensible. Only the latest version is
        returned.
        """
        # TODO: We should filter by organization

        # TODO: It would be preferable if we could return a regular django queryset here,
        # which in turn would return the wrapper when materialized. For that to work smoothly,
        # we'll need to look into implementation details of django querysets.

        # TODO: The `to_wrapper` method is NOT on this mixin, which makes this difficult to reason
        # about and error-prone, refactor
        return ResultIterator(self._all_qs(), self.to_wrapper)

    def _all_qs(self):
        """Returns a queryset for all extensible of a particular version or latest if nothing
        is supplied
        """

        # TODO: `all` should return a queryset that automatically wraps the Django object and
        # after that we can remove methods named `*_qs`.
        return self._archetype_version_class.objects.filter(latest=True).prefetch_related('properties')

    def search(self, search_string):
        qs = self._search_qs(search_string)
        return ResultIterator(qs, self.to_wrapper)

    def _search_qs(self, query):
        # TODO: We'll have the same api for projects and containers, but for now we'll keep this
        # here for simplicity

        # TODO: We will offload all search (and sorting) of substances (as well as other things)
        # to elastic. For now we throw an error if the search isn't just 'project.name:'

        # TODO: The api for searching will be elastic's, so we just have a super simple parsing
        # for now:

        if query is None:
            return self._all_qs()

        query = query.strip()
        query = query.split(" ")
        if len(query) > 1:
            raise NotImplementedError("Complex queries are not yet supported")

        query = query[0]
        key, val = query.split(":")

        # TODO: the search parameter indicates we're looking for a substance that's a sample
        # so add a category or similar so it doesn't find other things that are in a container.
        qs = self._archetype_version_class.objects.filter(
            latest=True, name__icontains=val).prefetch_related('properties')

        qs = qs.order_by('-archetype__created_at')
        return qs

    def filter_from(self, query_builder):
        query_params = query_builder.parse_query()
        return self.filter(**query_params)

    def filter(self, **kwargs):
        order_by_arg = kwargs.pop('order_by', None)
        get_args = self._get_filter_arguments(**kwargs)
        qs = self._archetype_version_class.objects.prefetch_related(
            Prefetch('properties', to_attr='all_properties'),
            Prefetch('all_properties__extensible_property_type')).\
            filter(**get_args)

        if order_by_arg:
            qs = qs.order_by(order_by_arg)

        return ResultIterator(qs, self.to_wrapper)

    def get(self, **kwargs):
        try:
            get_args = self._get_filter_arguments(**kwargs)
            model = self._archetype_version_class.objects.prefetch_related(
                Prefetch('properties', to_attr='all_properties'),
                Prefetch('all_properties__extensible_property_type')).\
                get(**get_args)
            return self.to_wrapper(model)
        except django_exceptions.ObjectDoesNotExist as e:
            # TODO-simple: Map to CLIMS exceptions in all service methods that use django, since
            # we don't want users to have to import from django.
            raise DoesNotExist(six.text_type(e))

    def _get_filter_arguments(self, **kwargs):
        get_args = {}
        if 'latest' not in kwargs.keys():
            kwargs['latest'] = True

        for key, value in kwargs.items():
            if key == 'project':
                get_args['archetype__project__name'] = value.name
            elif key == 'project_name':
                get_args['archetype__project__name'] = value
            elif key == 'latest':
                get_args['{}'.format(key)] = value
            elif key == 'id':
                get_args['archetype__{}'.format(key)] = value
            else:
                get_args['{}'.format(key)] = value
        return get_args

    @classmethod
    def _filter_by_extensible_version(cls, query_set):
        raise NotImplementedError("This method needs to be implemented by inheriting classes.")

    @classmethod
    def _property_query_set_and_property_value_field(cls, property):
        inital_query_set = ExtensibleProperty.objects.\
            filter(extensible_property_type__name=property)
        filtered_queryset = cls._filter_by_extensible_version(inital_query_set)
        prop_type = filtered_queryset.first()
        if not prop_type:
            raise DoesNotExist("No property of type: {} found".format(property))
        extensible_prop_type_value_field = prop_type.extensible_property_type.get_value_field()
        return (filtered_queryset, extensible_prop_type_value_field)

    @classmethod
    def get_values_of_property(cls, property):
        property_query_set, extensible_prop_type_value_field = \
            cls._property_query_set_and_property_value_field(property)
        values = property_query_set.values(extensible_prop_type_value_field).all()
        return [x[extensible_prop_type_value_field] for x in values]

    @classmethod
    def get_unique_values_of_property(cls, property):
        property_query_set, extensible_prop_type_value_field = \
            cls._property_query_set_and_property_value_field(property)

        unique_values = property_query_set.\
            order_by(extensible_prop_type_value_field).\
            distinct(extensible_prop_type_value_field)

        return {x.value for x in unique_values}


class BaseQueryBuilder:
    # TODO: decide internal query separators
    QUERY_SEPARATOR = "&&"

    def __init__(self, query_from_url):
        self.order_by = None
        self.query_from_url = query_from_url

    def order_by_created_date(self):
        self.order_by = '-archetype__created_at'

    def parse_query(self):
        query_params = dict()
        if self.order_by:
            query_params['order_by'] = self.order_by

        key, val = self._parse_query_from_url()
        if key:
            parsed_params = self.parse_params_for_class(key, val)
            query_params = dict(query_params, **parsed_params)
        return query_params

    @abstractmethod
    def parse_params_for_class(self, key, val):
        pass

    def _parse_query_from_url(self):

        query = self.query_from_url.strip() if self.query_from_url else []
        if len(query) == 0:
            return None, None
        query = query.split(BaseQueryBuilder.QUERY_SEPARATOR)

        if len(query) > 1:
            raise NotImplementedError("Complex queries are not yet supported")
        query = query[0]
        key, val = query.split(":")
        return key, val
