# Django REST framework 初探

## 项目创建说明

### 创建 app

```bash
python manage.py startapp myapp_api
```

### 定义数据模型并同步数据库

```python
"""
myapp_api/models.py
"""

from django.db import models

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    sex = models.CharField(max_length=10)
    age = models.IntegerField()
```

```bash
python manage.py makemigrations
python manage.py migrate
```

### 编写序列化器

```python
"""
myapp_api/serializers.py
"""

from myapp_api.models import User
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User    # 指定数据模型
        fields = '__all__'  # 显示所有字段
```

### 编写视图

```python
"""
myapp_api/views.py
"""

from django.shortcuts import render
from rest_framework import viewsets
from .serializers import UserSerializer
from myapp_api.models import User

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()   # 指定操作的数据
    serializer_class = UserSerializer   # 指定序列化器
```

### 添加 API 路由

```python
"""
Liang_test/urls.py
"""

# from django.contrib import admin
from django.urls import path, re_path, include

urlpatterns = [
    re_path('myapp_api/', include('myapp_api.urls'))
]
```

```python
"""
myapp_api/urls.py
"""

from django.urls import path, re_path, include
from myapp_api import views
from rest_framework import routers

# 自注册路由
router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet)

urlpatterns = [
    #    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
```

### 访问测试

```python
http://127.0.0.1:8000/myapp_api/api/user/
```