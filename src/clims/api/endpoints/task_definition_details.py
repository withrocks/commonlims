from __future__ import absolute_import

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sentry.api.base import Endpoint, DEFAULT_AUTHENTICATION
from clims.utils import single_or_default
from clims.api.serializers.models.task_definition import TaskDefinitionSerializer


class TaskDefinitionDetailsEndpoint(Endpoint):
    authentication_classes = DEFAULT_AUTHENTICATION
    permission_classes = (IsAuthenticated, )

    def get(self, request, process_definition_key, task_definition_key):
        task_definitions = self.app.workflows.get_task_definitions(
            process_definition_key, task_definition_key)
        ret = single_or_default(task_definitions)
        return Response(TaskDefinitionSerializer(ret).data)
