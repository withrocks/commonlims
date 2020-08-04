from __future__ import absolute_import

from rest_framework.permissions import IsAuthenticated

from sentry.api.base import DEFAULT_AUTHENTICATION
from rest_framework.response import Response
from rest_framework import status
from sentry.api.bases.organization import OrganizationEndpoint
from clims.api.serializers.script_trigger import ScriptTriggerSerializer


class TriggerScriptEndpoint(OrganizationEndpoint):
    authentication_classes = DEFAULT_AUTHENTICATION
    permission_classes = (IsAuthenticated, )

    def post(self, request, organization):
        # This endpoint is constructed in order to trigger a plugin script,
        # specified by input parameters.
        serializer = ScriptTriggerSerializer(data=request.data)
        if not serializer.is_valid():
            return self.respond(serializer.errors, status=400)

        step_name = serializer.validated_data.get('name')
        event_type = serializer.validated_data.get('event_type')
        event_tag = serializer.validated_data.get('event_tag')
        step_cls = self.app.workbatches.get_step_template(step_name)
        step = step_cls()
        step.trigger_script(event_type, event_tag, None)
        ret = {}
        return Response(ret, status=status.HTTP_201_CREATED)
