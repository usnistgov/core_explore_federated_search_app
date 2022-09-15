""" Result Serializers
"""
from rest_framework.serializers import CharField

from core_main_app.commons.serializers import BasicSerializer


class ResultDetailSerializer(BasicSerializer):
    """Result Detail Serializer"""

    id = CharField(required=True)
    instance_name = CharField(required=True)
