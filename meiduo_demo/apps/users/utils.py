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

    def authenticate(self, request, username=None, password=None, **kwargs):
        if request is None:
            # 后台登录
            user = self.check_admin_user(username)
            if user and user.check_password(password):
                return user

        else:
            try:
                if re.match(r'^1[3-9]\d{9}$', username):
                    user = User.objects.get(mobile=username)
                else:
                    user = User.objects.get(username=username)
                    # user = User.objects.get(username=username)
            except:
                # 如果未查到数据，则返回None，用于后续判断
                try:
                    user = User.objects.get(mobile=username)
                except:
                    return None
            if user.check_password(password):
                return user
            else:
                return None

    def check_admin_user(self, username):
        try:
            if re.match(r'^1[3-9]\d{9}$', username):
                user = User.objects.get(mobile=username, is_staff=True)
            else:
                user = User.objects.get(username=username, is_staff=True)
        except Exception as e:
            user = None
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
