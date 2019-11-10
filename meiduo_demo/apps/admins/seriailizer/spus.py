from rest_framework import serializers

from apps.goods.models import SPU, SPUSpecification


class SPUSerializer(serializers.ModelSerializer):
    """
        SPU表序列化器
        "brand": "品牌名称",
        "brand_id": "品牌id",
        "category1_id": "一级分类id",
        "category2_id": "二级分类id",
        "category3_id": "三级分类id",
    """
    # 商品品牌
    brand = serializers.StringRelatedField(read_only=True)
    brand_id = serializers.IntegerField()
    # 商品级别
    category1_id = serializers.IntegerField()
    category2_id = serializers.IntegerField()
    category3_id = serializers.IntegerField()

    class Meta:
        model = SPU

        fields = '__all__'