from rest_framework import serializers
from apps.goods.models import SpecificationOption


class SPUOptionsSerializer(serializers.ModelSerializer):
    # 关联返回
    spec = serializers.StringRelatedField(read_only=True)
    spec_id = serializers.IntegerField()

    class Meta:

        model = SpecificationOption

        fields = '__all__'