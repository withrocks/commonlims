from __future__ import absolute_import

from tests.clims.models.test_substance import SubstanceTestCase
from clims.plugins.demo.dnaseq.workflows.sequence import SequenceSimple
from clims.api.serializers.models.process_definition import ProcessDefinitionSerializer


class ProcessDefinitionSerializerTest(SubstanceTestCase):
    def test_simple(self):
        process = SequenceSimple()
        serializer = ProcessDefinitionSerializer(process)
        assert serializer.data == expected_sequence_simple


expected_sequence_simple = {
    'id':
    u'clims.plugins.demo.dnaseq.workflows.sequence.SequenceSimple',
    'fields': [{
        'display_name': u'Comment',
        'help': None,
        'required': False,
        'choices': [],
        'type': u'textarea',
        'name': u'comment'
    }, {
        'display_name': u'Sample prep',
        'help': u'The method used for preparing the sample',
        'required': True,
        'choices': ['microwave', 'mixer'],
        'type': u'select',
        'name': u'sample_prep'
    }, {
        'display_name': u'Sequencer',
        'help': u'Instrument where the sample will be sequenced',
        'required': True,
        'choices': ['iPhone', 'Android', 'Bang & Olufsen'],
        'type': u'select',
        'name': u'sequencer'
    }, {
        'display_name': u'Sample type',
        'help': u'The type of the sample',
        'required': True,
        'choices': ['DNA', 'RNA'],
        'type': u'select',
        'name': u'sample_type'
    }],
    'presets': [{
        'variables': {
            'sample_prep': 'microwave',
            'sequencer': 'Android',
            'sample_type': 'DNA'
        },
        'processDefinitionId':
        'clims.plugins.demo.dnaseq.workflows.sequence.SequenceSimple',
        'name': 'Android: DNA prepared with microwave'
    }, {
        'variables': {
            'sample_prep': 'mixer',
            'sequencer': 'Android',
            'sample_type': 'DNA'
        },
        'processDefinitionId':
        'clims.plugins.demo.dnaseq.workflows.sequence.SequenceSimple',
        'name': 'Android: DNA prepared with mixer'
    }, {
        'variables': {
            'sample_prep': 'microwave',
            'sample_type': 'DNA',
            'sequencer': 'iPhone'
        },
        'processDefinitionId':
        'clims.plugins.demo.dnaseq.workflows.sequence.SequenceSimple',
        'name': 'iPhone: DNA prepared with microwave'
    }, {
        'variables': {
            'sample_prep': 'microwave',
            'sequencer': 'Android',
            'sample_type': 'RNA'
        },
        'processDefinitionId':
        'clims.plugins.demo.dnaseq.workflows.sequence.SequenceSimple',
        'name': 'Android: RNA prepared with microwave'
    }, {
        'variables': {
            'sample_prep': 'microwave',
            'sample_type': 'DNA',
            'sequencer': 'Bang & Olufsen'
        },
        'processDefinitionId':
        'clims.plugins.demo.dnaseq.workflows.sequence.SequenceSimple',
        'name': 'Bang & Olufsen: DNA prepared with microwave'
    }, {
        'variables': {
            'sample_prep': 'mixer',
            'sequencer': 'Android',
            'sample_type': 'RNA'
        },
        'processDefinitionId':
        'clims.plugins.demo.dnaseq.workflows.sequence.SequenceSimple',
        'name': 'Android: RNA prepared with mixer'
    }]
}
