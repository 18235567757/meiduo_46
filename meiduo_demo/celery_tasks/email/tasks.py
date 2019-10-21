from celery_tasks.main import celery_app
from django.core.mail import send_mail
from apps.users.utils import *


@celery_app.task
def send_verify_email(user_id, email):

    # 标题
    subject = '美多商场激活邮件'
    # 内容
    message = ''
    # 发件人
    from_email = '美多商场<18235567757@163.com>'
    # 收件人列表
    recipient_list = [email]

    active_url = generic_active_email_url(user_id, email)

    html_message = '<p>您的邮箱为%s,请点击激活您的账号；<p>'\
        "<a href='%s'>%s</a>" % (email, active_url, active_url)
    send_mail(subject=subject,
              message=message,
              from_email=from_email,
              recipient_list=recipient_list,
              html_message=html_message)

