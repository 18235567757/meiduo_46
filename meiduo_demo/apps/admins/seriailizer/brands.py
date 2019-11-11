from rest_framework import serializers
from apps.goods.models import Brand


class BrandSerializer(serializers.ModelSerializer):
    """
    品牌序列化器
    """

    class Meta:
        model = Brand

        fields = '__all__'
