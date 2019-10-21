from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import cache

from apps.areas.models import Area

from django import http

from utils.response_code import RETCODE
from django.core.cache import cache


class AreasView(View):

    def get(self, request):
        # 接受到数据
        parent_id = request.GET.get('area_id')
        # 判断数据是否为空
        if parent_id is None:
            cache_pro = cache.get('cache_pro')

            if cache_pro is None:
                # 说明没有缓存
                # 拿到省份数据
                pro = Area.objects.filter(parent=None)
                # 将对象列表转换为字典列表
                # JsonResponse默认是可以对字典进行JSON转换的
                cache_pro = []
                for a in pro:
                    cache_pro.append({
                        'id':a.id,
                        'name':a.name

                    })

                # 设置缓存
                cache.set('cache_pro', cache_pro, 1)

            return http.JsonResponse({'code': RETCODE.OK, 'province_list': cache_pro})

        else:
            # 获取缓存
            city_list = cache.get('city_%s' % parent_id)
            if city_list is None:
                # 根据省的ID查询市,得到的是查询集
                pro = Area.objects.get(id=parent_id)
                cities = pro.subs.all()

                city_list = []
                for a in cities:
                    city_list.append({

                        'id':a.id,
                        'name':a.name
                    })

                cache.set('city_%s'% parent_id, city_list, 24*3600)

            # 返回响应
            return http.JsonResponse({'code':RETCODE.OK, 'subs': city_list})



