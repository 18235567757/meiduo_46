import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from apps.goods.models import SKU
from apps.orders.models import OrderInfo, OrderGoods
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
        total_amount = Decimal('0')

        freight = Decimal('10.00')

        # 支付方式
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return JsonResponse({'code':RETCODE.PARAMERR, 'errmsg':'支付方式错误'})

        if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']:
            status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        else:
            status = OrderInfo.ORDER_STATUS_ENUM['UNPAID']

        from django.db import transaction

        with transaction.atomic():

            savepoint = transaction.savepoint()
            try:
                order_info = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=total_count,
                    total_amount=total_amount,
                    freight=freight,
                    pay_method=pay_method,
                    status=status
                )
                # 再写入订单商品信息
                    # 获取redis中,指定用户的选中信息[1.2]
                redis_conn = get_redis_connection('carts')
                # 通过id获取到商品的购买数量
                id_counts = redis_conn.hgetall('carts_%s' % user.id)
                # 通过id获取到商品的选中状态
                selected_ids = redis_conn.smembers('selected_%s' % user.id)

                selected_dict = {}
                # 选中商品的id
                for id in selected_ids:
                    selected_dict[int(id)] = int(id_counts[id])

                for sku_id,count in selected_dict.items():
                    sku = SKU.objects.get(id=sku_id)
                    #说明库存不足
                    if sku.stock < count:
                        #回滚
                        transaction.savepoint_rollback(savepoint)

                        return JsonResponse({'code':RETCODE.STOCKERR,'errmsg':'库存不足'})
                    # import time
                    # time.sleep(7)

                    # 乐观锁
                    # 乐观所第一步，先记录库存
                    old_stock = sku.stock

                    # 乐观锁　第二步　计算更新后的数据
                    new_stock = sku.stock-count

                    new_sales = sku.sales=count

                    #　更新前,再判断一次，相同则更新数据
                    # 乐观锁第三步
                    rect = SKU.objects.filter(id=sku_id, stock=old_stock).update(stock=new_stock, sales=new_sales)

                    OrderGoods.objects.create(
                        order=order_info,
                        sku=sku,
                        count=count,
                        price=sku.price
                    )

                    order_info.total_count += count
                    order_info.total_amount += (count*sku.price)

                    order_info.save()
            except Exception as e:
                transaction.savepoint_rollback(savepoint)
            else:
                transaction.savepoint_commit(savepoint)

        return JsonResponse({'code':RETCODE.OK, 'errmsg':'ok',
                             'order_id':order_info.order_id,
                             'payment_amount':order_info.total_amount,
                             'pay_method':order_info.pay_method,
                            })


class OrderSuccessView(View):

    def get(self, request):

        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')

        context = {
            'order_id':order_id,
            'payment_amount':payment_amount,
            'pay_method':pay_method,
        }

        return render(request, 'order_success.html', context=context)