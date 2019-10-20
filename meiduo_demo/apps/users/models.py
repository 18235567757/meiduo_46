from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
"""
1.可以自己定义模型
    要实现密码的加密，密码的验证等功能
2.使用系统的模型（系统的模型可以帮助我们进行密码的加密和密码的验证）

"""


class User(AbstractUser):
    """自定义用户模型类"""
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
