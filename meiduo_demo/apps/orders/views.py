
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator

from django.shortcuts import render
from django import http
# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from apps.goods.models import SKU
from apps.orders.models import OrderInfo, OrderGoods
from apps.users.models import Address, User
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
            sku.count = selected_dict[id] # 数量
            sku.amount = (sku.price*sku.count) # 小计
            skus.append(sku)
            # 累加计算
            total_count += sku.count
            total_amount += sku.amount
        # 运费
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


class OrderCommitView(LoginRequiredMixin, View):

    def post(self,request):
        # 接收数据
        data = json.loads(request.body.decode())
        address_id = data.get('address_id')
        pay_method = data.get('pay_method')
        # 验证数据
        if not all([address_id, pay_method]):
            return http.JsonResponse({'code':RETCODE.PARAMERR, 'errmsg': '参数不齐全'})
        # 数据入库
        user = request.user

        try:
            address = Address.objects.get(id=address_id, user=user)
        except Address.DoesNotExist:
            return http.JsonResponse({'code':RETCODE.PARAMERR, 'errmsg': '地址不正确'})
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
            return http.JsonResponse({'code':RETCODE.PARAMERR, 'errmsg': '支付方式错误'})

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
                    # 说明库存不足
                    if sku.stock < count:
                        # 回滚
                        transaction.savepoint_rollback(savepoint)

                        return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})
                    # import time
                    # time.sleep(7)

                    # 乐观锁
                    # 乐观所第一步，先记录库存
                    old_stock = sku.stock

                    # 乐观锁　第二步　计算更新后的数据
                    new_stock = sku.stock-count

                    new_sales = sku.sales=count

                    # 更新前,再判断一次，相同则更新数据
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

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok',
                                 'order_id': order_info.order_id,
                                  'payment_amount': order_info.total_amount,
                                  'pay_method': order_info.pay_method,
                            })


class OrderSuccessView(View):

    def get(self, request):

        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')

        context = {
            'order_id': order_id,
            'payment_amount': payment_amount,
            'pay_method': pay_method,
        }

        return render(request, 'order_success.html', context=context)


class InfoView(LoginRequiredMixin, View):

    def get(self, request, page_num):
        # 获取到用户的订单数据,并且进行倒序排序
        order_list = request.user.orders.order_by('-create_time')
        # 创建分页器,每页５条记录
        paginator = Paginator(order_list, 5)
        # 获取当前页的数据
        page = paginator.page(page_num)

        # 通过for循环拿到当前页数据的详细信息
        order_list2=[]
        for order in page:
            detail_list = []
            for detail in order.skus.all():
                detail_list.append({
                    'default_image_url': detail.sku.default_image.url,
                    'name': detail.sku.name,
                    'price': detail.price,
                    'count': detail.count,
                    'total_amount': detail.price * detail.count,
                })

            order_list2.append({
                'order_id': order.order_id,
                'create_time': order.create_time,
                'details': detail_list,
                'total_amount': order.total_amount,
                'freight': order.freight,
                'status': order.status,

            })
        context = {
            'page':order_list2,
            'page_num':page_num,
            'total_page':paginator.num_pages
        }

        return render(request, 'user_center_order.html', context)


class CommentView(LoginRequiredMixin, View):

    def get(self, request):
        # 获取用户订单id信息
        order_id = request.GET.get('order_id')
        # 查询订单商品列表
        try:
            order = OrderInfo.objects.get(pk=order_id, user_id=request.user.id)

        except OrderInfo.DoesNotExist:
            return http.HttpResponseBadRequest('此商品不存在')
        # 获取订单的所有商品
        skus = []
        for detail in order.skus.filter(is_commented=False):
            skus.append({
                'sku_id': detail.sku_id,
                'name': detail.sku.name,
                'price': str(detail.price),
                'order_id': order_id,
                'default_image_url': detail.sku.default_image.url,
            })

        context = {
            'skus': skus

        }

        return render(request, 'goods_judge.html', context)

    def post(self, request):

        data = json.loads(request.body.decode())

        comment = data.get('comment')
        order_id = data.get('order_id')
        score = data.get('score')
        sku_id = data.get('sku_id')
        is_anonymous = data.get('is_anonymous')
        # 判断数据是否齐全
        if not all([comment, order_id, score, sku_id]):
            return http.JsonResponse({'code':RETCODE.PARAMERR, 'errmsg':'参数不完整'})
        # 判断is_anonymous值的类型是否为bool类型
        if not isinstance(is_anonymous, bool):
            return http.JsonResponse({'code':RETCODE.PARAMERR, 'errmsg':'is_anonymous参数类型错误'})
        # 创建实例对象
        order_goods = OrderGoods.objects.get(sku=sku_id, order_id=order_id)
        # 添加修改数据
        order_goods.comment = comment
        order_goods.score = int(score)
        order_goods.is_anonymous = is_anonymous
        order_goods.is_commented = True
        # 提交保存
        order_goods.save()

        return http.JsonResponse({'code':RETCODE.OK, 'errmsg':'ok'})


class CommentSKUView(LoginRequiredMixin, View):

    def get(self, request, sku_id):

        # 查询指定sku_id的所有评论信息
        comments = OrderGoods.objects.filter(sku_id=sku_id, is_commented=True)
        comment_list = []
        # detail表示OrderGoods对象
        for detail in comments:
            username = detail.order.user.username
            if detail.is_anonymous:
                username = '******'
            comment_list.append({
                'username': username,
                'comment': detail.comment,
                'score': detail.score
            })

        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': "OK",
            'goods_comment_list': comment_list
        })


