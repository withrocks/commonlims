from __future__ import absolute_import

from rest_framework import serializers


class ProcessDefinitionFieldSerializer(serializers.Serializer):
    # Serializes one field in a workflow process definition
    pass


class ExtensibleBaseFieldSerializer(serializers.Serializer):
    name = serializers.CharField()
    required = serializers.BooleanField()
    choices = serializers.ListField()
    help = serializers.CharField()
    type = serializers.CharField()
    # TODO: It would be nice to change display_name to label everywhere
    display_name = serializers.CharField()


class ProcessDefinitionSerializer(serializers.Serializer):
    id = serializers.CharField()
    fields = serializers.SerializerMethodField(
        method_name="get_serialized_fields")
    presets = serializers.SerializerMethodField()

    def get_serialized_fields(self, obj):
        return [
            ExtensibleBaseFieldSerializer(x).data for x in obj.get_fields()
        ]

    def get_presets(self, obj):
        mapped_presets = list()
        for key, preset in obj.get_presets().items():
            mapped_preset = dict()
            mapped_preset["processDefinitionId"] = obj.id
            mapped_preset["name"] = key
            mapped_preset["variables"] = preset
            mapped_presets.append(mapped_preset)
        return mapped_presets
