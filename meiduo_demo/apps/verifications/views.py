# Create your views here.
from django.views import View

from libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django import http

class ImageCodeView(View):

    def get(self, request, uuid):
        # 生成图片验证码
        text, image = captcha.generate_captcha()
        # 保存图片验证码
        redis_conn = get_redis_connection('code')
        redis_conn.setex('img_%s' % uuid, 120, text)

        # 响应返回图片验证码
        return http.HttpResponse(image, content_type='image/jpeg')