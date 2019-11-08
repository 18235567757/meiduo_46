from rest_framework import serializers

from apps.orders.models import OrderInfo


class OrderInfoserializer(serializers.ModelSerializer):
    class Meta:
        model = OrderInfo

        fields = '__all__'
