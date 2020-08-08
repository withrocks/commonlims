from __future__ import absolute_import

from sentry.testutils import APITestCase
from clims.plugins.demo.dnaseq import DemoDnaSeqPlugin


class TaskDefinitionTest(APITestCase):
    endpoint = 'clims-api-0-task-definitions'

    def setUp(self):
        self.clean_workflow_engine_state()
        self.app.plugins.install_plugins(DemoDnaSeqPlugin)
        self.has_context()

    def test_get(self):
        from clims.plugins.demo.dnaseq.workflows.sequence import SequenceSimple
        from clims.plugins.demo.dnaseq.models import ExamplePlate, ExampleSample

        # Install with plugin API
        sample_count = 2
        cont = ExamplePlate(name="cont1")
        for x in range(1, sample_count + 1):
            sample = ExampleSample(name="sample-{}".format(x))
            cont.append(sample)
        cont.save()
        workflow = SequenceSimple()
        workflow.assign(cont)

        # Get through REST API
        self.login_as(self.user)
        response = self.client.get(self.get_url())
        expected = [{
            "id": "clims.plugins.demo.dnaseq.workflows.sequence.SequenceSimple/data_entry",
            "count": sample_count,
            "name": "Data entry",
            "processDefinitionKey": "clims.plugins.demo.dnaseq.workflows.sequence.SequenceSimple",
            "processDefinitionName": "SequenceSimple",
            "taskDefinitionKey": "data_entry",
        }]

        assert response.status_code == 200
        assert expected == response.data
