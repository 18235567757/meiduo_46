from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.contens.models import ContentCategory
from apps.contens.utils import get_categories


class IndexView(View):

    def get(self, request):
        """提供首页广告界面"""
        # 查询商品频道和分类
        categories = get_categories()

        contents = {}

        content_categorice = ContentCategory.objects.all()
        for cat in content_categorice:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

        # 渲染模板的上下文
        context = {
            'categories': categories,
            'contents': contents,
        }

        return render(request, 'index.html', context=context)

#
# from fdfs_client.client import Fdfs_client
#
# client = Fdfs_client('utils/fastdfs/client.conf')
#
# client.upload_by_filename('/home/python/Desktop/image/1.jpg')