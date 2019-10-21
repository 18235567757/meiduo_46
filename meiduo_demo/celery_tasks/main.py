# celery启动文件
from celery import Celery

# 为celery使用django配置文件进行设置
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_demo.settings")

# 创建celery实例
celery_app = Celery('celery_tasks')

# 设置中间人
celery_app.config_from_object('celery_tasks.config')

# 让celery自动检测我们的任务
# 列表元素的值就是任务的包路径
celery_app.autodiscover_tasks(['celery_task.sms', 'celery_task.email'])

# 运行消费者

# 语法　celery -A proj worker -l infoex
# proj 指的是celery实力对象的脚本路径
# celery -A celery_tasks.main worker -l info
