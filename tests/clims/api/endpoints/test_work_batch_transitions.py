from __future__ import absolute_import

import json

from retry import retry
from django.core.urlresolvers import reverse

from sentry.testutils import APITestCase

from clims.plugins.demo.dnaseq import DemoDnaSeqPlugin
from clims.plugins.demo.dnaseq.models import ExamplePlate, ExampleSample
from clims.plugins.demo.dnaseq.workflows.sequence import SequenceSimple


class WorkBatchTransitionsEndpointTest(APITestCase):
    def setUp(self):
        """
        Installs the demo plugin in a clean environment.
        """
        self.clean_workflow_engine_state()
        self.app.plugins.install_plugins(DemoDnaSeqPlugin)
        self.has_context()

    def test_simple(self):
        # Here we'll create a workbatch that doesn't connect to any workflow engine.
        tasks = ["local/new"]
        work_batch = self.app.workflows.create_work_batch(tasks, self.organization)
        print(work_batch)
        # work_batch = WorkBatchSerializer(work_batch).data
        # url = reverse("clims-api-0-work-batch-transitions", kwargs={"work_batch_id": 1})
        # print(url)
        return

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

        response = self.client.post(
            path=url,
            data=json.dumps(tasks),
            content_type='application/json',
        )
        assert response.status_code == 201
