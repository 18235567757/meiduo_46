"""meiduo_demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from django.http import HttpResponse


def test(request):
    # 导入日志模块儿
    import logging

    # 创建日志记录器
    logger = logging.getLogger('django')

    # 输出日志
    logger.debug('测试logging模块儿debug')
    logger.info('测试loggin模块儿logger')
    logger.error('测试logging模块儿error')

    return HttpResponse('test')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^test/$', test),
    url(r'^', include('apps.users.urls', namespace='users')),
    url(r'^', include('apps.contens.urls', namespace='contens')),
]
