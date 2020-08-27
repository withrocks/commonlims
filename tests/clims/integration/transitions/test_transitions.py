"""
Integration tests for transitions. When a Substance either moves or a children is created from it,
a Transition is created. Plugins are called to validate the Transition.

Note that Transitions are *not* created when a Substance's value is changed. That creates a new
version of the Substance but doesn't create a Transition.
"""

# from retry import retry
# import pytest
# from clims.models import SubstanceAssignment
# from sentry.testutils import TestCase
# from sentry.models import ApiToken
# from clims.models import Workflow
from clims.plugins.demo.dnaseq.models import ExamplePlate, ExampleSample
from clims.plugins.demo.dnaseq.workflows.sequence import SequenceSimple
from clims.utils import single
from django.core.urlresolvers import reverse
from sentry.testutils import APITestCase


class TestTransitions(APITestCase):
    def setUp(self):
        """
        Installs the demo plugin in a clean environment.
        """
        self.clean_workflow_engine_state()
        self.install_main_demo_plugin()
        self.has_context()

    def test__when_analyte_created__plugin_raises_validation_error_if_so_configured(self):
        self.toggle_log_level()
        self.login_as(self.user, superuser=True)  # TODO: Should not have to be superuser

        c1 = ExamplePlate(name="C1")
        s1 = ExampleSample(name="S1")
        c1.append(s1)
        c1.save()

        # Now, we'll assign the sample to a workflow...
        workflow = SequenceSimple()
        workflow.comment = "Let's sequence some stuff"
        workflow.assign(c1)  # Assigns all samples in the container to the workflow

        # ... and wait for it to end up in a UserTask
        task = single(workflow.wait_for_usertasks("data_entry", 1))
        print("HERE", task)
        # response = self.client.post(url, {})
        # print(response)

        # Assign the task (single) to a WorkBatch. This simulates what would happen in the
        # UI if the user
        # (1) Opens Available Work
        # (2) Selects a type of UserTask waiting
        # (3) Selects a single item from the list and presses Start Work

        url = reverse('clims-api-0-work-batches', kwargs={'organization_slug': 'lab'})
        resp = self.client.post(url, data=[task.id])
        assert resp.status_code == 201

        # Now, the caller (e.g. web UI) might show a default output plate for each input plate
        # but it does not exist in the backend until there is at least one transition.
        # Here we create a transition from s1@c1 =A=> s1.1@c2 via the rest api:

        url = reverse('clims-api-0-work-batch-transitions')
        print(url)
