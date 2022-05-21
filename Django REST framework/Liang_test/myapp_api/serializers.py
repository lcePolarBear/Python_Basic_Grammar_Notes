from myapp_api.models import User
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User    # 指定数据模型
        fields = '__all__'  # 显示所有字段