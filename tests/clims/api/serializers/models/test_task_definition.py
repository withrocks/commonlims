from __future__ import absolute_import

from tests.clims.models.test_substance import SubstanceTestCase
from clims.api.serializers.models.task_definition import TaskDefinitionSerializer
from clims.services.workflow import TaskDefinitionInfo


class ProcessDefinitionSerializerTest(SubstanceTestCase):
    def test_simple(self):
        task_definition_info = TaskDefinitionInfo("id", "name", "pdkey", "tdkey", "pdname", 3)
        serializer = TaskDefinitionSerializer(task_definition_info)

        assert serializer.data == {
            "id": "id",
            "name": "name",
            "processDefinitionKey": "pdkey",
            "taskDefinitionKey": "tdkey",
            "processDefinitionName": "pdname",
            "count": 3
        }
