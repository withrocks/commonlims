from __future__ import absolute_import

from sentry.api.paginator import OffsetPaginator
from sentry.api.bases.organization import OrganizationEndpoint
from clims.api.serializers.models.task_definition import TaskDefinitionSerializer


class TaskDefinitionEndpoint(OrganizationEndpoint):
    def get(self, request, organization):
        task_definitions = self.app.workflows.get_task_definitions()

        return self.paginate(
            request=request,
            queryset=task_definitions,
            paginator_cls=OffsetPaginator,
            on_results=lambda entry: TaskDefinitionSerializer(entry, many=True).data,
        )
