from __future__ import absolute_import

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sentry.api.base import Endpoint, SessionAuthentication


class ProcessAssignmentsEndpoint(Endpoint):
    authentication_classes = (SessionAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, organization_slug):
        """
        Assign one or more item to a workflow. The items are assigned by global_id.
        """

        # TODO-auth: Ensure that the user is only assigning samples that are under the organization

        # Entities is a list of global ids (e.g. Substance-100)
        entities = request.data["entities"]
        definition = request.data["definitionId"]
        variables = request.data["variables"]

        assignments = list()

        assignments += self.app.workflows.batch_assign(
            entities, definition, request.user, variables)

        return Response({"assignments": len(assignments)}, status=201)
