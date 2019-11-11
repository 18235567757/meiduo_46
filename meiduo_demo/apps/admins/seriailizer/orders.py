from rest_framework import serializers

from apps.orders.models import OrderInfo, OrderGoods
from apps.goods.models import SKU


class SKUSerializer(serializers.ModelSerializer):
    """
    商品sku表序列化器
    """

    class Meta:
        model = SKU
        fields = ('name', 'default_image')


class OrderGoodsSerializer(serializers.ModelSerializer):
    """
    订单商品序列化器
    """
    sku = SKUSerializer()

    class Meta:
        model = OrderGoods

        fields = ('count', 'price', 'sku')


class OrderInfoserializer(serializers.ModelSerializer):
    """
    订单基本信息序列化器
    """
    skus = OrderGoodsSerializer(many=True)

    class Meta:
        model = OrderInfo

        fields = '__all__'
