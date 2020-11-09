from __future__ import absolute_import

from sentry.testutils import TestCase

from clims.api.serializers.models.work_batch_details_definition import WorkBatchDetailsDefinitionSerializer
from clims.services.workbatch import WorkBatchBase
from clims.configuration.hooks import button


class WorkBatchDetailsDefintionSerializerTest(TestCase):
    def setUp(self):
        self.has_context()
        self.register_extensible(MyFancyStep)

    def test_can_serialize_work_definition(self):
        workbatch = MyFancyStep()
        result = WorkBatchDetailsDefinitionSerializer(workbatch).data
        assert result.get('id') == 'serializers.models.test_work_batch_details_definition.MyFancyStep'
        assert result.get('cls_full_name') == 'serializers.models.test_work_batch_details_definition.MyFancyStep'
        assert result.get('name') == 'My fancy step'
        assert result.get('buttons') == [{'caption': 'My submit button', 'event': 'on_button_click1'}]


class MyFancyStep(WorkBatchBase):
    name = 'My fancy step'

    @button('My submit button')
    def on_button_click1(self):
        setattr(MyFancyStep, 'was_called', True)
