from django.db import transaction
from rest_framework import serializers

from apps.goods.models import SKU, GoodsCategory, SpecificationOption, SPUSpecification, SKUSpecification


class SKUSpecificationSerializer(serializers.ModelSerializer):
    """
        SKU规格表序列化器
    """

    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()

    class Meta:
        model = SKUSpecification

        fields = ("spec_id", 'option_id')


class SKUserializer(serializers.ModelSerializer):
    """
        SKU商品序列化器

    """

    spu = serializers.StringRelatedField(read_only=True)
    category = serializers.StringRelatedField(read_only=True)
    spu_id = serializers.IntegerField()
    category_id = serializers.IntegerField()

    specs = SKUSpecificationSerializer(many=True)

    class Meta:
        model = SKU

        fields = '__all__'

    def create(self, validated_data):
        # 获取specs数据
        specs = validated_data['specs']
        # 将specs数据从validated_data中删除
        del validated_data['specs']
        with transaction.atomic():
            ser = transaction.savepoint()
            try:
                # 将数据添加到sku表中
                sku = super().create(validated_data)
                # 保存sku具体规格表数据
                for spec in specs:
                    SKUSpecification.objects.create(sku=sku, spec_id=spec['spec_id'], option_id=spec['option_id'])
            except:
                transaction.savepoint_rollback(ser)
                raise serializers.ValidationError('保存失败')
                # 返回数据
                return sku

    def update(self, instance, validated_data):

        # 获取specs数据
        specs = validated_data['specs']
        # 将specs数据从validated_data中删除
        with transaction.atomic():
            sid = transaction.savepoint()
            try:
                del validated_data['specs']
                # 将数据添加到sku表中
                sku = super().update(instance, validated_data)
                # 修改sku具体规格表数据
                for spec in specs:
                    SKUSpecification.objects.update(sku=sku, spec_id=spec['spec_id']).update(option_id=spec['option_id'])
            except:
                transaction.savepoint_rollback(sid)
                raise serializers.ValidationError('修改失败')
                # 返回数据
            else:
                return sku


class GoodsCategorySerializer(serializers.ModelSerializer):
    """
    商品类别序列化器

    """

    class Meta:
        model = GoodsCategory

        fields = '__all__'


class SpecificationOptionSerializer(serializers.ModelSerializer):
    """

    商品规格选项序列化器

    """

    class Meta:
        model = SpecificationOption

        fields = ('id', 'value')


class SPUSpecificationSerializer(serializers.ModelSerializer):
    """

    商品规格序列化器
    """
    # 关联嵌套返回，返回规格是将规格选项一块返回 父表嵌套子表返回
    options = SpecificationOptionSerializer(many=True)

    # 将关联的spu数据返回 子表嵌套父表
    spu = serializers.StringRelatedField(read_only=True)
    spu_id = serializers.IntegerField()

    class Meta:
        model = SPUSpecification

        fields = '__all__'
