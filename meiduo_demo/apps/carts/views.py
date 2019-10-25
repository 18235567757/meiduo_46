import base64
import http
import json
import pickle

from django import http

from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from apps.goods.models import SKU
from utils.response_code import RETCODE

"""

1. 如果用户未登录,可以实现添加购物车的功能.
   如果用户登录,也可以实现添加购物车的功能.

2.如果用户未登录, 我们要保存 商品id,商品数量,商品的选中状态
  如果用户登录, 我们要保存 用户id, 商品id,商品数量,商品的选中状态

3.如果用户未登录,  保存在 浏览器中   cookie中
  如果用户登录,    保存在数据库中   (为了让大家更好的学习redis)我们把数据保存到redis中


4. 如果用户未登录,  cookie的数据格式
    {
        sku_id:{count:5,selected:True},
        sku_id:{count:2,selected:False},
        sku_id:{count:7,selected:True},
    }

    如果用户登录, Redis  .Redis的数据是保存在内存中,
    我们要尽量少的占用内存空间

    user_id ,sku_id,count,selected

    1,          100,2,True
                101,5,False
                102,10,True
                103,10,False



    key         100:2
                selected_100:True

                101:5
                selected_101:False

                102:10
                selected_102:True

                103:10
                selected_103:False

            hash
    user_id     100:2
                101:5
                102:10
                103:10
            set  选中的在集合中
selected_user_id   [100,102]


                hash
    user_id     100:2
                101:-5
                102:10
                103:-10


5.

{
    sku_id:{count:5,selected:True},
    sku_id:{count:2,selected:False},
    sku_id:{count:7,selected:True},
}

base64


1G = 1024MB
1M=1024KB
1KB=1024B
1B=8bite 比特位  0  1

A   0100 0001

0100 0001   0100 0001   0100 0001
A               A           A


010000     010100   000101     000001
x               y    z          a


  5.1 将字典转换为二进制

  5.2 再进行base64编码

"""

from django.contrib.auth.mixins import LoginRequiredMixin


class CartsView(View):

    """
    1.功能分析
    用户行为:
    前端行为:       当用户点击加入购物车的时候,前端要收集用户信息,sku_id,count,默认是选中
    后端行为:

    2. 分析后端实现的大体步骤

        1.接收数据,判断商品信息
        2.先获取用户信息
        3.根据用户是否登陆来判断
        4.登陆用户操作数据(redis)
            4.1 连接数据库
            4.2 操作数据库
            4.3 返回相应
        5.未登录用户操作cookie
            5.1 组织数据
            5.2 对数据进行编码
            5.3 设置cookie
            5.4 返回相应
        6.返回相应

    3.确定请求方式和路由
        POST        carts
    """

    def post(self, request):
        # 1.接收数据,判断商品信息
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        count = data.get('count')
        if not all([sku_id, count]):
            return http.JsonResponse({'code':RETCODE.PARAMERR, 'errmsg': '参数不全' })
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.JsonResponse({'code':RETCODE.NODATAERR, 'errmsg': '没有此商品'})

        try:
            count = int(count)
        except Exception:
            return http.JsonResponse({'code':RETCODE.PARAMERR, 'errmsg': '参数错误'})

        selected = True

        # 2.先获取用户信息
        user = request.user
        # 3.根据用户是否登陆来判断
        if user.is_authenticated:
            # 4.登陆用户操作数据(redis)
            #     4.1 连接数据库
            redis_conn = get_redis_connection('carts')
            #     4.2 操作数据库
            redis_conn.hset('carts_%s' %user.id, sku_id, count)
            redis_conn.sadd('selecten_%s' % user.id, sku_id)
            #     4.3 返回相应
            return http.JsonResponse({'code':RETCODE.OK, "errmsg":'OK'})
        else:
            # 5.未登录用户操作cookie
            #     5.1 组织数据
            carts_str = request.COOKIES.get('carts')
            if carts_str is None:
                cookie_data = {
                    sku_id:{'count': count, 'selected': True}
                }
            else:
                decode_data = base64.b64decode(carts_str)
                #　在bytes转字典
                cookie_data = pickle.loads(decode_data)

                if sku_id in cookie_data:
                    origin_count = cookie_data[sku_id]['count']
                    count+=origin_count
                    cookie_data[sku_id] = {'count':count, 'selected':True}
                else:
                    cookie_data[sku_id] = {'count':count, 'selected':True}
            #     5.2 对数据进行编码
            #     字典转bytes
            cookie_bytes = pickle.dumps(cookie_data)
            #     base64编码
            cookie_str = base64.b64encode(cookie_bytes)
            #     5.3 设置cookie
            response = http.JsonResponse({'code':RETCODE.OK, 'errmsg':'ok'})

            response.set_cookie('carts', cookie_str, max_age=3600)
            #     5.4 返回相应
            return response