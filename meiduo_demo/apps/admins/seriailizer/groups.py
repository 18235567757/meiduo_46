from rest_framework import serializers
from django.contrib.auth.models import Group


class GroupSerializer(serializers.ModelSerializer):
    """
    用户权限序列化器
    """

    class Meta:
        model = Group
        fields = '__all__'
