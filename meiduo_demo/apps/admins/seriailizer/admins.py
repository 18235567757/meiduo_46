from rest_framework import serializers
from apps.users.models import User
import re


class AdminSerializers(serializers.ModelSerializer):
    class Meta:
        model = User

        fields = '__all__'

        extra_kwargs = {
            'password': {
                'write_only': True,
                'max_length': 20,
                'min_length': 8,
                'required': False,


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
        user.is_staff = True
        user.save()

        return user

    def update(self, instance, validated_data):
        # 调用父类更新方法
        instance = super().update(instance, validated_data)
        # 判断是否修改密码
        password = validated_data.get('password')
        if password:
            instance.set_password(validated_data['password'])
            instance.save()

        return instance
