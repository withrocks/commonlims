from __future__ import absolute_import

import re
import logging
from django.db import transaction
from rest_framework.response import Response

from sentry.api.exceptions import ResourceDoesNotExist
from sentry.api.paginator import OffsetPaginator
from sentry.api.serializers import serialize
from sentry.models import File
from clims.models import WorkBatch, WorkBatchFile
from clims.api.bases.work_batch import WorkBatchBaseEndpoint

ERR_FILE_EXISTS = 'A file matching this name already exists for the given WorkBatch'
_filename_re = re.compile(r"[\n\t\r\f\v\\]")


class WorkBatchTransitionsEndpoint(WorkBatchBaseEndpoint):
    def get(self, request, work_batch_id):
        """
        List transitions in a WorkBatch
        ````````````````````````

        Example:

        curl --header "Authorization: Bearer $LIMS_TOKEN" \
                      "http://localhost:8000/api/0/work-batches/1/transitions/"

        :pparam string work_batch_id: the ID of the user task
        :auth: required
        """
        try:
            work_batch = WorkBatch.objects.get(pk=work_batch_id)
        except WorkBatch.DoesNotExist:
            raise ResourceDoesNotExist

        raise NotImplementedError()

        file_list = WorkBatchFile.objects.filter(
            work_batch=work_batch,
        ).select_related('file', 'dist').order_by('name')

        return self.paginate(
            request=request,
            queryset=file_list,
            order_by='name',
            paginator_cls=OffsetPaginator,
            on_results=lambda x: serialize(x, request.user),
        )

    def post(self, request, work_batch_id):
        """
        Upload a new transition related to a WorkBatch
        ``````````````````````````````````````````````

        Upload a new transition in the context of a WorkBatch.

        :pparm string work_batch_id: the id of the task
        :param string name: the name (full path) of the file.
        :auth: required
        """

        from sentry.models.workbatch import WorkBatch

        try:
            work_batch = WorkBatch.objects.get(pk=int(work_batch_id))
        except WorkBatch.DoesNotExist:
            raise ResourceDoesNotExist
        print(work_batch)

