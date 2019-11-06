from django.conf.urls import url
from .utils import jwt_response_payload_handler

urlpatterns = [
    url(r'^authorizations/$', jwt_response_payload_handler),
]