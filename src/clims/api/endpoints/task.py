from __future__ import absolute_import


from sentry.api.paginator import OffsetPaginator
from sentry.api.bases.organization import OrganizationEndpoint


class UserTaskAggregateEndpoint(OrganizationEndpoint):
    def get(self, request, organization):
        from clims.models import CamundaTask
        from django.db.models import Count
        tasks = CamundaTask.objects.select_related('process')
        tasks_count = tasks.values(
            'name',
            'process__name',
            'process__key').annotate(
            count=Count('name'))

        def serialize(entries):
            # A serializer that renames e.g. process__name to processName.
            # TODO_django1.8: use the F function instead https://stackoverflow.com/a/32580991
            def rename_keys(entry):
                new_entry = dict()
                for key in entry:
                    if "__" in key:
                        a, b = key.split("__")
                        new_key = a + b.capitalize()
                    else:
                        new_key = key
                    new_entry[new_key] = entry[key]
                return new_entry
            return [rename_keys(entry) for entry in entries]

        return self.paginate(
            request=request,
            queryset=tasks_count,
            paginator_cls=OffsetPaginator,
            on_results=lambda entry: serialize(entry),
        )