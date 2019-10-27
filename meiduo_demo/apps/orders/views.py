import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from apps.goods.models import SKU
from apps.orders.models import OrderInfo
from apps.users.models import Address
from utils.response_code import RETCODE


class PlaceOrderView(LoginRequiredMixin, View):

    def get(self, request):
        # 购物车结算视图必须是登录用户才可以展示
        user = request.user
        # 获取登陆用户的地址信息
        addresses = Address.objects.filter(user=user, is_deleted=False)
        # 连接redis数据库
        redis_conn = get_redis_connection('carts')

        id_count = redis_conn.hgetall('carts_%s' %user.id)

        selected_ids = redis_conn.smembers('selected_%s' % user.id)
        # 循环便利拿到redis登陆用户选中的商品信息
        selected_dict = {}
        # 使用bytes进行类型转换
        for id in selected_ids:
            selected_dict[int(id)] = int(id_count[id])
        # 根据商品信息,回去商品详细信息
        ids = selected_dict.keys()

        skus = []
        # 准备初始值
        total_count = 0
        total_amount = 0

        for id in ids:
            sku = SKU.objects.get(id=id)
            sku.count = selected_dict[id]# 数量
            sku.amount = (sku.price*sku.count)# 小计
            skus.append(sku)
            # 累加计算
            total_count += sku.count
            total_amount += sku.amount
        #　运费
        freight = 10

        context = {
            'addresses': addresses,
            'skus': skus,
            # 以下的几个 复制过来
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount': total_amount + freight
        }

        return render(request, 'place_order.html', context=context)


class OrderCommitView(LoginRequiredMixin,View):

    def post(self,request):
        # 接收数据
        data = json.loads(request.body.decode())
        address_id = data.get('address_id')
        pay_method = data.get('pay_method')
        # 验证数据
        if not all([address_id, pay_method]):
            return JsonResponse({'code':RETCODE.PARAMERR, 'errmsg':'参数不齐全'})
        # 数据入库
        user = request.user

        try:
            address = Address.objects.get(id=address_id,user=user)
        except Address.DoesNotExist:
            return JsonResponse({'code':RETCODE.PARAMERR,'errmsg':'地址不正确'})
            # 拼接订单编号
        from django.utils import timezone

        order_id = timezone.localtime().strftime('%Y%m%d%H%H%S')+'%09d'%user.id
        # 总数量0,　总金额0,　运费
        total_count = 0
        from decimal import Decimal
        total_amout = Decimal('0')

        freeight = Decimal('10.00')

        # 支付方式
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]
            return JsonResponse({'code':RETCODE.PARAMERR, 'errmsg':'支付方式错误'})

        if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']:
            status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        else:
            status = OrderInfo.ORDER_STATUS_ENUM['UNPAID']
        

        #
        #