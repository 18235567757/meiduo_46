from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.users.models import User
# Create your views here.
from datetime import date, timedelta
from apps.admins.seriailizer.statistical import GoodsCountSerializers
from apps.goods.models import GoodsVisitCount


class UserTotalCountView(APIView):
    def get(self, request):

        count = User.objects.filter(is_staff=False).count()

        return Response({
            'count': count
        })


class UserDayCountView(APIView):

    def get(self, request):

        """
        日增用户统计
        :param request:
        :return:
        """
        now_data = date.today()

        count = User.objects.filter(is_staff=False, date_joined__gte=now_data).count()

        return Response({
            'count': count
        })


class UserDayActiveCountView(APIView):

    def get(self, request):

        """
        日活跃用户统计
        :param request:
        :return:
        """

        today = date.today()

        count = User.objects.filter(is_staff=False, last_login__gte=today).count()

        return Response({
            'count': count
        })


class UserDayOrdersCountView(APIView):

    def get(self, request):

        """
        日下单用户统计
        :param request:
        :return:
        """

        today = date.today()

        count = User.objects.filter(orders__create_time__gte=today).count()

        return Response({
            'count': count
        })


class UserMonthCountView(APIView):

    def get(self, request):

        """
        月增用户统计
        :param request:
        :return:
        """

        today = date.today()

        old_date = today - timedelta(30)

        date_list = []

        for i in range(30):
            # 获取当天信息
            index_date = old_date+timedelta(i)
            # 获取下一天信息
            next_date = old_date+timedelta(i+1)

            count = User.objects.filter(is_staff=False, date_joined__gte=index_date, date_joined__lt=next_date).count()

            date_list.append({
                'count': count,
                'date': index_date,
            })
            return Response(date_list)


class GoodsCountView(ListAPIView):

    serializer_class = GoodsCountSerializers

    queryset = GoodsVisitCount.objects.filter(date=date.today())