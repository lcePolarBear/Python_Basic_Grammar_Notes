from django.shortcuts import render
from rest_framework import viewsets
from .serializers import UserSerializer
from myapp_api.models import User

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()   # 指定操作的数据
    serializer_class = UserSerializer   # 指定序列化器