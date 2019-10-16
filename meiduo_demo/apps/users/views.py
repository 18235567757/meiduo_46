from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.views import View
import re
from django import http



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
        if not re.match(r'^[a-zA-Z0-9]{5,20}$', username):
            return http.HttpResponseBadRequest('请输入5-20个字符的用户名')
        # 判断密码是否为8-20个字符
        if not re.match(r'^[0-9a-zA-Z]{8,20}$', password):
            return http.HttpResponseBadRequest('请输入8-20位的密码')
        if password!=password2:
            return http.HttpResponseBadRequest('两次输入的密码不一样')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('请输入正确的手机号')
        # 判断是否勾选用户协议
        if allow != 'on':
            return http.HttpResponseBadRequest('请勾选用户协议')

        User.objects.create_user(username=username,
                                 password=password,
                                 mobile=mobile,
                                 )
        return HttpResponse('OK')
