from __future__ import absolute_import

import json

from retry import retry
from django.core.urlresolvers import reverse

from sentry.testutils import APITestCase

from clims.plugins.demo.dnaseq import DemoDnaSeqPlugin
from clims.plugins.demo.dnaseq.models import ExamplePlate, ExampleSample
from clims.plugins.demo.dnaseq.workflows.sequence import SequenceSimple


class WorkBatchEndpointTest(APITestCase):
    def setUp(self):
        """
        Installs the demo plugin in a clean environment.
        """
        self.clean_workflow_engine_state()
        self.app.plugins.install_plugins(DemoDnaSeqPlugin)
        self.has_context()

    def test_simple(self):
        url = reverse('clims-api-0-work-batches',
                      args=(self.organization.name, ))
        self.login_as(self.user)

        sample_count = 3

        cont = ExamplePlate(name="cont1")
        for x in range(1, sample_count + 1):
            sample = ExampleSample(name="sample-{}".format(x))
            cont.append(sample)
        cont.save()

        workflow = SequenceSimple()
        workflow.comment = "Let's sequence some stuff"
        workflow.assign(cont)

        # TODO-medium: The high-level API should provide the task_types via `workflow.task_types`
        # and all pending tasks via `workflow.tasks`

        # Now, make sure that we've reached the manual work stage. It's possible, albeit unlikely
        # that the workflow hasn't reached that step yet, so we retry on failure

        @retry(AssertionError, tries=2, delay=1)
        def get_tasks():
            tasks = self.app.workflows.get_tasks(
                task_definition_key="data_entry",
                process_definition_key=workflow.id)
            tracked_objects_in_workflow_engine = [
                t.tracked_object.id for t in tasks
            ]
            assert len(tracked_objects_in_workflow_engine) == sample_count
            return tasks

        tasks = get_tasks()
        tasks = [t.id for t in tasks]

        payload = {
            "tasks": tasks,
        }

        response = self.client.post(
            path=url,
            data=json.dumps(payload),
            content_type='application/json',
        )
        assert response.status_code == 201
