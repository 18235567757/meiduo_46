from rest_framework import serializers
from django.contrib.auth.models import Permission, ContentType


class PermissionSerializer(serializers.ModelSerializer):
    """
    用户权限序列化器
    """

    class Meta:
        model = Permission
        fields = '__all__'


class ContentTypeSerializer(serializers.ModelSerializer):
    """
    获取权限类型
    """
    name = serializers.CharField()

    class Meta:
        model = ContentType
        fields = '__all__'
