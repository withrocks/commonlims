from __future__ import absolute_import

from rest_framework import serializers

from clims.api.serializers.models.substance import SubstanceSerializer
from clims.services.substance import SubstanceBase


class TaskSerializer(serializers.Serializer):
    id = serializers.CharField()
    tracked_object = serializers.SerializerMethodField()

    def get_tracked_object(self, obj):
        # TODO: Create field type for this
        if isinstance(obj.tracked_object, SubstanceBase):
            return SubstanceSerializer(obj.tracked_object).data
        else:
            raise AssertionError("Can't serialize tracked object: {}".format(
                obj.tracked_object))
