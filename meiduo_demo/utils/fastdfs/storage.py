from django.core.files.storage import Storage

from meiduo_demo import settings


class FastDFSStorage(Storage):
    """
    自定义文件存储系统
    """

    # def __init__(self, fdfs_base_url=None):
    #     self.fdfs_base_url = fdfs_base_url or settings.FDFS_BASE_URL

    def _open(self):
        pass

    def _save(self):
        pass

    def url(self, name):

        return "http://192.168.131.138:8888/" + name
