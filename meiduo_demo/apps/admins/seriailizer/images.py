from rest_framework import serializers
from apps.goods.models import SKUImage, SKU
from fdfs_client.client import Fdfs_client


class SKUImageSerializer(serializers.ModelSerializer):
    # 关联返回

    class Meta:

        model = SKUImage

        fields = '__all__'

    def create(self, validated_data):
        # 获取前端sku对象
        sku = validated_data['sku']
        # 获取前端传递的图片数据
        image = validated_data['image']
        # 链接fastDSF
        client = Fdfs_client('/home/python/Desktop/meiduo_46/meiduo_demo/utils/fastdfs/client.conf')
        # 上传图片
        ret = client.upload_by_buffer(image.read())
        # 判断是否成功
        if ret['Status'] != 'Upload successed.':
            raise serializers.ValidationError('上传失败')
        # 提取图片链接地址
        path = ret.get('Remote file_id')
        # 保存图片表
        img = SKUImage.objects.create(sku=sku, image=path)

        return img

    def update(self, instance, validated_data):
        # 获取前端sku对象
        sku = validated_data['sku']
        # 获取前端传递的图片数据
        image = validated_data['image']
        # 链接fastDSF
        client = Fdfs_client('/home/python/Desktop/meiduo_46/meiduo_demo/utils/fastdfs/client.conf')
        # 上传图片
        ret = client.upload_by_buffer(image.read())
        # 判断是否成功
        if ret['Status'] != 'Upload successed.':
            raise serializers.ValidationError('上传失败')
        # 提取图片链接地址
        path = ret.get('Remote file_id')
        # 更新图片表

        instance.image = path
        instance.save()

        return instance

class SKUSerializer(serializers.ModelSerializer):
    # 关联返回

    class Meta:

        model = SKU

        fields = '__all__'