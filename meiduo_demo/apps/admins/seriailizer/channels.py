from rest_framework import serializers
from apps.goods.models import GoodsChannel, GoodsChannelGroup, GoodsCategory


class GoodsCategorySerializer(serializers.ModelSerializer):
    """
    商品类别序列化器
    """

    class Meta:
        model = GoodsCategory
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    """
    商品组类别序列化器
    """

    class Meta:
        model = GoodsChannelGroup
        fields = '__all__'


class ChannelsSerializer(serializers.ModelSerializer):
    """
    商品频道序列化器
    """
    group_id = serializers.IntegerField(read_only=True)

    group = serializers.StringRelatedField(read_only=True)
    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = GoodsChannel

        fields = '__all__'
