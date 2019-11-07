from rest_framework import serializers
from apps.goods.models import SKUImage, SKU


class SKUImageSerializer(serializers.ModelSerializer):
    # 关联返回

    class Meta:

        model = SKUImage

        fields = '__all__'


class SKUSerializer(serializers.ModelSerializer):
    # 关联返回

    class Meta:

        model = SKU

        fields = '__all__'