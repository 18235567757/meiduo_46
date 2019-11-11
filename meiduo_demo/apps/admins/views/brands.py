from rest_framework.viewsets import ModelViewSet

from apps.admins.seriailizer.brands import BrandSerializer
from apps.admins.utils import pagenum
from apps.goods.models import Brand


class BrandView(ModelViewSet):
    serializer_class = BrandSerializer

    queryset = Brand.objects.all()

    pagination_class = pagenum

    # def categories(self, request):
    #     return
