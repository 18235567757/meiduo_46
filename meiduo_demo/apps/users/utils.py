import re

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import authenticate

from apps.users.models import User
import logging
logger = logging.getLogger('django')


def get_user_by_usernamemobile(username):
    try:
        if re.match(r'^1[3-9]\d{9}$', username):
            # 手机号登录
            user = User.objects.get(mobile=username)
        else:
            # 用户名登录
            user = User.objects.get(username=username)
    except Exception as e:
        logger.error(e)
        return None
    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):

    # def authenticate(self, request, username=None, password=None, **kwargs):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 1.区分用户名和手机号
        # try:
        #     if re.match(r'^1[3-9]\d{9}$', username):
        #         # 手机号登录
        #         user = User.objects.get(mobile=username)
        #     else:
        #         # 用户名登录
        #         user = User.objects.get(username=username)
        # except Exception as e:
        #     logger.error(e)
        # else:
        # user = get_user_by_usernamemobile(username)
        #
        # if user is not None and user.check_password(password):
        #     return user
        if request is None:
            # 后台登录
            try:
                if re.match(r'1[3-9]\d{9}', username):
                    # 手机号登陆
                    user = User.objects.get(mobile=username, is_staff=True)
                else:
                    # 用户名登陆
                    user = User.objects.get(username=username, is_staff=True)
            except:
                user = None
            if user is not None and user.check_password(password):
                return user
        else:
            # 前台登录

            # 1. 区分 手机号 和 用户名
            # try:
            #     if re.match(r'1[3-9]\d{9}',username):
            #         # 手机号登陆
            #         user = User.objects.get(mobile=username)
            #     else:
            #         # 用户名登陆
            #         user=User.objects.get(username=username)
            # except Exception as e:
            #     logger.error(e)
            #     return None
            # else:
            # 1.就要一个用户名
            user = get_user_by_usernamemobile(username)
            # 2.检查密码
            if user is not None and user.check_password(password):
                return user

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from meiduo_demo import settings
from itsdangerous import BadData
# 'http://www.meiduo.site:8000/emailsactive/?token=%s'%token


def generic_active_email_url(id,email):
    # 创建加密实例对象
    s = Serializer(secret_key=settings.SECRET_KEY,expires_in=3600)
    # 组织数据
    data = {
        'id':id,
        'email':email,
    }
    # 加密
    serect_data = s.dumps(data)

    # 返回数据
    return 'http://www.meiduo.site:8000/emailsactive/?token=%s' % serect_data.decode()


def check_active_token(token):
    # 创建实例对象
    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)

    # 解密
    try:
        data = s.loads(token)
    except BadData:
        return None

    # 返回数据
    return data
