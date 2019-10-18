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
    def authenticate(self, request, username=None, password=None, user=None, **kwargs):
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
        user = get_user_by_usernamemobile(username)

        if user is not None and user.check_password(password):
            return user