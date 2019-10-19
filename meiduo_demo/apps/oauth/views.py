from django.contrib.auth import login
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse

from django.views import View

from django import http
from QQLoginTool.QQtool import OAuthQQ

from apps.oauth.models import OAuthQQUser
from apps.users.utils import logger
from meiduo_demo import settings


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
            return render(request, 'oauth_callback.html')
        else:
            login(request, qquser.user)
            response = redirect(reverse('contens:index'))

            response.set_cookie('username',qquser.user.username, max_age=24*3600)

            return response

    def post(self, request):

        # ①接收数据
        # ②验证数据  openid
        #     参数是否齐全
        #     手机号是否符合规则
        #     密码是否符合规则
        #     短信验证码是否一致
        # ③根据手机号进行用户信息的查询  user
        #     如果存在,则需要验证密码
        #     如果不存在,说明用户手机号没有注册过,我们就以这个手机号注册一个用户
        # ④ 绑定openid 和 user
        # ⑤ 登陆(设置登陆状态,设置cookie,跳转到首页)

        pass

        try:
            qquser = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            pass
        else:
            qq_user = qquser.user
            login(request, qq_user)

            next = request.GET.get('state')

            response = redirect(next)

            response.set_cookie('username', qq_user.username, max_age=24*3600)