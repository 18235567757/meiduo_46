import re

from django.contrib.auth import login
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse

from django.views import View

from django import http
from QQLoginTool.QQtool import OAuthQQ

from apps.oauth.models import OAuthQQUser
from apps.users.models import User
from apps.users.utils import logger
from meiduo_demo import settings
from django_redis import get_redis_connection
import redis
class QQloginView(View):

    def get(self, request):

        code = request.GET.get('code')

        if code is None:
            return http.HttpResponseBadRequest('没有code')
        oauthqq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state='xxxx'
                        )

        # login_url =oauthqq.get_qq_url()

        token= oauthqq.get_access_token(code)

        openid = oauthqq.get_open_id(token)

        try:
            qquser = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            return render(request, 'oauth_callback.html', context={'openid': openid})
        else:
            login(request, qquser.user)
            response = redirect(reverse('contens:index'))

            response.set_cookie('username', qquser.user.username, max_age=24*3600)

            return response

    def post(self, request):

        # ①接收数据
        mobile = request.POST.get('mobile')
        pwd = request.POST.get('pwd')
        sms_code = request.POST.get('sms_code')
        openid = request.POST.get('openid')

        # ②验证数据  openid
        #     参数是否齐全
        if not all([mobile, pwd]):
            return http.HttpResponseBadRequest('参数不全')
        # 手机号是否符合规则
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('您的手机号填写有误')
        # 密码是否符合规则
        if not re.match(r'[a-zA-Z0-9_]{8,20}$', pwd):
            return http.HttpResponseBadRequest('您的密码不合法')
        #     短信验证码是否一致
        redis_conn = get_redis_connection('code')
        sms_code_conn = redis_conn.get('img_%' % mobile)
        if sms_code_conn is None:
            return http.HttpResponseBadRequest('无效的短信验证码')
        if sms_code != sms_code_conn.decode():
            return http.HttpResponseBadRequest('短信验证码输入错误')

        # ③根据手机号进行用户信息的查询  user
        try:
            user = User.objects.get(mobile=mobile)
        # 如果不存在,说明用户手机号没有注册过,我们就以这个手机号注册一个用户
        except User.DoesNotExist:
            user = User.objects.create_user(mobile=mobile,
                                          password=pwd,
                                          username=mobile)
        # 如果存在,则需要验证密码
        else:
            if not user.check_password(pwd):
                return http.HttpResponseBadRequest('密码错误')

        # ④ 绑定openid 和 user
        OAuthQQUser.objects.create(user=user, openid=openid)
        # ⑤ 登陆(设置登陆状态,设置cookie,跳转到首页)
        login(request, user)

        response = redirect(reverse('contens:index'))

        response.set_cookie('username', user.username, max_age=3600*24)

        return response