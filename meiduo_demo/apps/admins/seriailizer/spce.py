from rest_framework import serializers
from apps.goods.models import SPUSpecification, SPU


class SPUSpceSerializer(serializers.ModelSerializer):
    # 关联返回
    spu = serializers.StringRelatedField(read_only=True)
    spu_id = serializers.IntegerField()

    class Meta:

        model = SPUSpecification

        fields = '__all__'


class SPUSerializer(serializers.ModelSerializer):

    """
    商品SPU序列化器
    """

    class Meta:

        model = SPU

        fields = '__all__'