from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection

from apps.goods.models import SKU
from apps.users.models import Address


class PlaceOrderView(LoginRequiredMixin,View):

    def get(self, request):

        user = request.user

        addresses = Address.objects.filter(user=user,is_deleted=False)

        redis_conn = get_redis_connection('carts')

        id_count = redis_conn.hgetall('carts_%s' %user.id)

        selected_ids = redis_conn.smembers('selected_%s' % user.id)

        selected_dict = {}

        for id in selected_ids:
            selected_dict[int(id)] = int(id_count[id])

        ids = selected_dict.keys()

        skus = []

        total_count = 0
        total_amount = 0

        for id in ids:
            sku = SKU.objects.get(id=id)
            sku.count = selected_dict[id]
            sku.amount = (sku.price*sku.count)
            skus.append(sku)
            # 累加计算
            total_count += sku.count
            total_amount += sku.amount

        freight = 10

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
