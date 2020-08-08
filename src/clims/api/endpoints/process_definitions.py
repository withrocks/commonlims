from __future__ import absolute_import

import logging
from rest_framework.permissions import IsAuthenticated

from clims.api.serializers.models.process_definition import ProcessDefinitionSerializer
from sentry.api.base import SessionAuthentication
from sentry.api.base import Endpoint
from sentry.api.paginator import OffsetPaginator

logger = logging.getLogger(__name__)


class ProcessDefinitionsEndpoint(Endpoint):
    authentication_classes = (SessionAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        # TODO: At the moment, all workflow definitions are application-wide, not organization-wide
        # Fetch all loaded workflows in the system:
        # TODO: Paging by using the ResultIterator
        processes = list(self.app.workflows.get_process_definitions())

        return self.paginate(request=request,
                             queryset=processes,
                             paginator_cls=OffsetPaginator,
                             default_per_page=20,
                             on_results=lambda data:
                             ProcessDefinitionSerializer(data, many=True).data)
