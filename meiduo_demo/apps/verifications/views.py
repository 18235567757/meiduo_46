# Create your views here.
import base64
import json
import pickle

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from apps.users.models import User
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django import http
from django.http import HttpResponseBadRequest

from libs.yuntongxun.sms import CCP
from utils.response_code import RETCODE


class ImageCodeView(View):

    def get(self, request, uuid):
        # 生成图片验证码
        text, image = captcha.generate_captcha()
        # 保存图片验证码
        # 链接redis数据库
        redis_conn = get_redis_connection('code')
        redis_conn.setex('img_%s' % uuid, 120, text)

        # 响应返回图片验证码
        return http.HttpResponse(image, content_type='image/jpeg')


class SMSCodeView(View):
    """短信验证码"""

    def get(self, reqeust, mobile):
        # 获取数据
        image_code = reqeust.GET.get('image_code')
        image_code_id = reqeust.GET.get('image_code_id')
        # 验证数据
        if not all([image_code, image_code_id]):
            return HttpResponseBadRequest('参数不全')
            # 省略用户验证码长度验证

        # 比对用户输入的验证码和redis的验证码是否一致
        from django_redis import get_redis_connection
        # 链接redis数据库
        redis_conn = get_redis_connection('code')
        # 获取指定的数据
        redis_text = redis_conn.get('img_%s' % image_code_id)

        if redis_text is None:
            return HttpResponseBadRequest('图片验证码已失效')
        redis_text = redis_text.decode()
        if redis_text.lower() != image_code.lower():
            return HttpResponseBadRequest('图片验证码不一致')

        # 生成一个随机短信验证码
        # 六位数值
        from random import randint
        sms_code = '%06d' % randint(0, 999999)
        # 保存短信验证码
        redis_conn.setex('sms_%s' % mobile, 120, sms_code)
        # 发送短信
        from celery_tasks.sms.tasks import send_sms_code
        send_sms_code.delay(mobile, sms_code)
        # 返回响应
        return JsonResponse({'msg': 'OK', 'code': '0'})


class PwdImageView(View):
    def get(self, request, username):

        uuid = request.GET.get('image_code_id')
        image_code = request.GET.get('text')

        redis_conn = get_redis_connection('code')

        image_code_id = redis_conn.get('img_%s' %uuid)

        if image_code_id is None:
            return http.JsonResponse({'code':RETCODE.IMAGECODEERR, 'errmsg':'图形验证码不存在，请点击图片更换一个吧！'})

        redis_conn.delete(uuid)

        if image_code_id.decode().lower() != image_code.lower():
            return http.JsonResponse({'code':RETCODE.PARAMERR, 'errmsg':'验证码错误'})

        try:
            user = User.objects.get(username=username)

        except User.DoesNotExist:
            return http.JsonResponse({'code':RETCODE.NODATAERR, 'errmsg':'此用户不存在'})

        access_token = base64.b64encode(pickle.dumps({'mobile':user.mobile,'user_id':user.id,})).decode()
        # access_token = {'mobile': user.mobile, 'user_id': user.id, }
        return http.JsonResponse({'mobile':user.mobile, 'access_token':access_token, })


class PwdSmsView(View):

    def get(self, request):
        data = request.GET.get('access_token')

        access_token = pickle.loads(base64.b64decode(data))
        if access_token is None:
            return http.JsonResponse({'code':RETCODE.NODATAERR, 'errmsg':'验证信息已失效'})

        mobile = access_token['mobile']

        try:
            User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            return http.JsonResponse({'code':RETCODE.NODATAERR, 'errmsg':'手机号错误'})

        from random import randint
        sms_code = '%06d' % randint(0, 999999)
        print(sms_code)
        # 保存短信验证码
        redis_conn = get_redis_connection('code')
        redis_conn.setex('sms_%s' % mobile, 120, sms_code)
        # 发送短信
        from celery_tasks.sms.tasks import send_sms_code
        send_sms_code.delay(mobile, sms_code)
        # 返回响应
        return JsonResponse({'code':RETCODE.OK, 'errmsg':'ok'})


class PwdCheckCodeView(View):

    def get(self, request, username):

        data = request.GET.get('sms_code')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return http.JsonResponse({'code':RETCODE.NODATAERR, 'errmsg':'用户名错误'})

        redis_conn = get_redis_connection('code')

        sms_code = redis_conn.get('sms_%s' % user.mobile)

        if sms_code is None:
            return http.JsonResponse({'code':RETCODE.NODATAERR, 'errmsg':'验证码以过期'})

        redis_conn.delete(user.mobile)
        redis_conn.delete('sms_%s', user.mobile)

        if data != sms_code.decode():
            return http.JsonResponse({'code':RETCODE.NODATAERR, 'errmsg':'短信验证码错误'})

        access_token = base64.b64encode(pickle.dumps({'mobile': user.mobile, 'user_id': user.id, })).decode()
        # access_token = {'mobile': user.mobile, 'user_id': user.id, }
        return http.JsonResponse({'mobile': user.mobile, 'user_id':user.id, 'access_token': access_token, })
