# Create your views here.
from django.http import JsonResponse
from django.views import View

from libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django import http
from django.http import HttpResponseBadRequest

from libs.yuntongxun.sms import CCP


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
        CCP().send_template_sms(mobile, [sms_code, 5],1)
        # 返回响应
        return JsonResponse({'msg': 'OK', 'code': '0'})