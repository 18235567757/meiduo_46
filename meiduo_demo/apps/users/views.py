import base64
import json
import pickle

from django.contrib.auth import login, logout
from django.http import HttpResponseBadRequest
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.users.models import User, Address
from django.http import HttpResponse
# from django.shortcuts import render,redirect
from django.contrib.auth import authenticate
# Create your views here.
from django.shortcuts import redirect, render

from django.views import View
import re
from django import http

from apps import users
from utils.response_code import RETCODE


class RegisterView(View):
    # 用户注册

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        data = request.POST
        username = data.get('username')
        password = data.get('password')
        password2 = data.get('password2')
        mobile = data.get('mobile')
        allow = data.get('allow')
        # 判断参数是否齐全
        if not all([username, password, password2, mobile, allow]):
            return http.HttpResponseBadRequest('缺少必传参数')
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_]{5,20}$', username):
            return http.HttpResponseBadRequest('请输入5-20个字符的用户名')
        # 判断密码是否为8-20个字符
        if not re.match(r'^[0-9a-zA-Z]{8,20}$', password):
            return http.HttpResponseBadRequest('请输入8-20位的密码')
        if password != password2:
            return http.HttpResponseBadRequest('两次输入的密码不一样')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('请输入正确的手机号')
        # 判断是否勾选用户协议
        if allow != 'on':
            return http.HttpResponseBadRequest('请勾选用户协议')

        user = User.objects.create_user(username=username,
                                 password=password,
                                 mobile=mobile,
                                 )

        login(request, user)
        return redirect(reverse('contens:index'))


class UsernameCountView(View):
    """
    判断用户名是否重复注册
    """
    def get(self, request, username):

        count=User.objects.filter(username=username).count()

        return http.JsonResponse({'code': 200, 'errmsg': 'OK', 'count': count})


class MobileCountView(View):
    #  判断手机号是否重复
    def get(self,request, mobile):
        count=User.objects.filter(mobile=mobile).count()

        return http.JsonResponse({'code': 200, 'errmsg': 'OK', 'count': count})


# 用户登录
class LogView(View):

    def get(self, request):

        return render(request, 'login.html')

    def post(self, request):

        data = request.POST
        username = data.get('username')
        password = data.get('pwd')
        remb = data.get('remembered')

        if not all([username, password, remb]):
            return HttpResponseBadRequest('缺少必传参数')
        if not re.match(r'^[a-z0-9A-Z]{5,20}$', username):
            return http.HttpResponseBadRequest('您的用户名不合法')
        if not re.match(r'^[a-z0-9A-Z_]{8,20}$', password):
            return http.HttpResponseBadRequest('你的密码输入不合法')

        # user = authenticate(username=username, password=password)
        user = authenticate(username=username, password=password)
        if user is None:
            return http.HttpResponseBadRequest('请输入正确的用户名或密码')
        login(request, user)
        if remb != 'on':
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(None)
        # 405 没有实现对应的方法

        response = redirect(reverse('contens:index'))

        response.set_cookie('username', user.username, max_age=3600*24*14)

        from apps.carts.utils import merge_cookie_to_redis
        response = merge_cookie_to_redis(request, user, response)

        return response


class LogoutView(View):

    def get(self, request):

        # 清理session
        logout(request)
        response = redirect(reverse('contens:index'))

        response.delete_cookie('username')
        return response


class UserCenterInfo(LoginRequiredMixin, View):

    def get(self, request):
        context = {
            'username':request.user.username,
            'mobile':request.user.mobile,
            'email':request.user.email,
            'email_active':request.user.email_active
        }

        # netx = request.GET.get('next')
        #
        # if netx:
        #     response = redirect(next)
        #
        # else:
        #     response = redirect(reverse('users:login'))

        return render(request, 'user_center_info.html', context=context)


class EmailView(View):

    def put(self, request):
        # 拿到数据
        json_dict = json.loads(request.body.decode())
        email = json_dict.get('email')
        # 校验参数
        if not email:
            return http.HttpResponseBadRequest('缺少email参数')
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseBadRequest('参数email有误')
        # 更新数据
        request.user.email = email
        request.user.save()
        # from django.core.mail import send_mail
        # # 标题
        # subject = '你好'
        # # 内容
        # message ='我是xxx'
        # # 发件人
        # from_email ='qi_rui_hua@163.com'
        # # 收件人列表
        # recipient_list= ['18235567757@163.com']
        #
        # html_message = "<a href='http://www.meiduo.site:8000/emailsactive/?user_id=1'>戳我有惊喜</a>"
        # send_mail(subject=subject,
        #           message=message,
        #           from_email=from_email,
        #           recipient_list=recipient_list,
        #           html_message=html_message)

        # try:
        #     User.objects.create(email=email)
        # except Exception:
        #     return http.JsonResponse({'code':0, 'errmsg': '添加邮箱失败'})
        from celery_tasks.email.tasks import send_verify_email
        send_verify_email.delay(request.user.id, email)

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加邮箱成功'})

from apps.users.utils import *


class EmailActiveView(View):

    def get(self, request):
        # 获取token信息
        token = request.GET.get('token')

        if token is None:
            return http.HttpResponseBadRequest('缺少参数')
        # 信息解密
        data = check_active_token(token)

        if data is None:
            return http.HttpResponseBadRequest('认证失败')
        # 根据用户信息进行数据的更新
        id = data.get('id')
        email = data.get('email')

        try:
            user = User.objects.get(id=id, email=email)
        except User.DoesNotExist:
            return http.HttpResponseBadRequest('验证失败')

        user.email_active = True
        user.save()

        # 跳转到指定页面
        return redirect(reverse('users:conter'))


class AddressView(LoginRequiredMixin, View):
    """用户收货地址"""
    def get(self, request):
        login_user = request.user
        addresses = Address.objects.filter(user=login_user, is_deleted=False)

        address_dict_list = []
        for address in addresses:
            address_dict = {
                    "id": address.id,
                    "title": address.title,
                    "receiver": address.receiver,
                    "province": address.province.name,
                    "province_id":address.province_id,
                    "city": address.city.name,
                    "city_id":address.city_id,
                    "district": address.district.name,
                    "district_id":address.district_id,
                    "place": address.place,
                    "mobile": address.mobile,
                    "tel": address.tel,
                    "email": address.email,
            }
            address_dict_list.append(address_dict)

        context = {
            'default_address_id': login_user.default_address_id,
            'addresses': address_dict_list

        }
        # """提供收货地址界面"""
        return render(request, 'user_center_site.html', context)


class CreateAddressView(LoginRequiredMixin, View):

    def post(self, request):

        count = request.user.addresses.count()
        if count >= 20:
            return http.JsonResponse({'code':RETCODE.THROTTLINGERR, 'errmsg':'超过地址数量上限'})

        # 接受参数
        json_dick = json.loads(request.body.decode())

        receiver = json_dick.get('receiver')
        province_id = json_dick.get('province_id')
        city_id = json_dick.get('city_id')
        district = json_dick.get('district_id')
        place = json_dick.get('place')
        mobile = json_dick.get('mobile')
        tel = json_dick.get('tel')
        email = json_dick.get('email')

        # 校验参数

        if not all([receiver, province_id, city_id, district, place, mobile]):
            return http.HttpResponseBadRequest('缺少必传参数')

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('您的手机号不合法')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseBadRequest('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseBadRequest('参数email有误')

        # 保存地址信息
        try:
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )

            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()

        except Exception as e:
            print(e)
            return http.JsonResponse({'code':RETCODE.DBERR, 'errmsg':'新增地址失败'})

        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email,

        }

        return http.JsonResponse({'code':RETCODE.OK, 'errmsg':'新增地址成功','address':address_dict})


class FindPasswordView(View):

    def get(self, request):

        return render(request, 'find_password.html', )


class ChangePwdView(View):
    def post(self, request, user_id):
        data = json.loads(request.body.decode())

        password = data.get('password')
        password2 = data.get('password2')
        data_token = data.get('access_token')
        access_token = pickle.loads(base64.b64decode(data_token))

        if password != password2:
            return http.JsonResponse({'code':RETCODE.PARAMERR, 'errmsg':'两次输入的密码不一样'})

        if access_token is None:
            return http.JsonResponse({'code':RETCODE.NODATAERR, 'errmsg':'验证信息已失效'})

        if int(user_id) != access_token['user_id']:
            return http.JsonResponse({'code':RETCODE.PARAMERR, 'errmsg':'用户id错误'})

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return http.JsonResponse({'code':RETCODE.PARAMERR, 'errmsg':'此用户不存在'})

        user.set_password(password)
        user.save()

        return http.JsonResponse({'code':RETCODE.OK, 'errmsg':'ok'})



