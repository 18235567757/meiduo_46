from fdfs_client.client import Fdfs_client
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.admins.seriailizer.spus import SPUSerializer, BrandSerializer, GoodsCategorySerializer
from apps.admins.utils import pagenum
from apps.goods.models import SPU, Brand, GoodsCategory


class SPUView(ModelViewSet):
    # 指定序列化器
    serializer_class = SPUSerializer
    # 指定查询结果集
    queryset = SPU.objects.all()
    # 指定分页器
    pagination_class = pagenum

    # 获取商品品牌信息
    def brand(self, request):
        data = Brand.objects.all()

        ser = BrandSerializer(data, many=True)

        return Response(ser.data)

    # 获取一级分类
    def channel(self, request):
        data = GoodsCategory.objects.filter(parent=None)

        ser = GoodsCategorySerializer(data, many=True)

        return Response(ser.data)

    # 获取二级分类
    def channel2(self, request, pk):
        data = GoodsCategory.objects.filter(parent=pk)

        ser = GoodsCategorySerializer(data, many=True)

        return Response(ser.data)

    def images(self, request):

        image = request.data.get('image')

        if image is None:
            return Response(status=500)

        # 链接fastDSF
        client = Fdfs_client('/home/python/Desktop/meiduo_46/meiduo_demo/utils/fastdfs/client.conf')
        # 上传图片
        ret = client.upload_by_buffer(image.read())
        # 判断是否成功
        if ret['Status'] != 'Upload successed.':
            return Response({'error': '上传失败'}, status=501)
        # 提取图片链接地址
        path = ret.get('Remote file_id')
        # 返回结果
        return Response({
            'img_url': 'http://192.168.131.138:8888/' + path
        })