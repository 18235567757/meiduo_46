from rest_framework import serializers
from apps.users.models import User
import re

class UserSerializers(serializers.ModelSerializer):

    class Meta:

        model = User

        fields = ('id', 'username', 'mobile', 'email', 'password')

        extra_kwargs = {
            'password': {
                'write_only': True,
                'max_length': 20,
                'min_length': 8,

            },
            'username': {
                'max_length': 20,
                'min_length': 5,
            }
        }

    def validate_mobile(self, attrs):
        """
        # 验证手机号
        :param attrs:
        :return:
        """
        if not re.match(r'^1[3-9]\d{9}', attrs):
            raise serializers.ValidationError('手机号不正确')

        return attrs

    def create(self, validated_data):
        # 调用父类保存方法
        user = super().create(validated_data)

        user.set_password(validated_data['password'])
        user.save()

        return user
