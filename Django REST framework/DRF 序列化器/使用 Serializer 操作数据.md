# 使用 Serializer 操作数据

## 使用 Serializer 查询所有数据

### 定义序列化器

```python
"""
myapp_api/serializers.py
"""

from rest_framework import serializers

class UserSerializer(serializers.Serializer):

    # 字段与使用的模型字段须相对应
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=30)
    city = serializers.CharField(max_length=30)
    sex = serializers.CharField(max_length=10)
    age = serializers.IntegerField()
```

### View 使用序列化器

```python
"""
myapp_api/views.py
"""

from .serializers import UserSerializer
from myapp_api.models import User
from rest_framework.response import Response
from rest_framework.views import APIView

class UserView(APIView):
    def get (self, request):
        # 获取所有用户
        queryset = User.objects.all()
        # 调用序列化器将 queryset 转化为 json
        user_ser = UserSerializer(queryset, many=True)
        # 从.data 属性获取序列化结果
        return Response(user_ser.data)
```

### 定义路由

```python
"""
myapp_api/urls.py
"""

from django.urls import path, re_path
from myapp_api import views

urlpatterns = [
    re_path('^api/user/$', views.UserView.as_view())
]
```

## 使用 Serializer 获取单个数据

接口地址：

```python
/myapp_api/api/user/2
```

### 定义视图

```python
"""
myapp_api/views.py
"""

from .serializers import UserSerializer
from myapp_api.models import User
from rest_framework.response import Response
from rest_framework.views import APIView

class UserView(APIView):
    def get (self, request, pk=None):
        if pk:
            # 获取单个用户
            user_obj = User.objects.get(id=pk)
            user_ser = UserSerializer(user_obj)
        else:
            # 获取所有用户
            user_obj = User.objects.all()
            # 调用序列化器将 queryset 转化为 json
            user_ser = UserSerializer(user_obj, many=True)
        # 从.data 属性获取序列化结果
        result = {'code': 200, 'message': '获取用户数据成功', 'data': user_ser.data}
        return Response(result)
```

### 定义路由

```python
"""
myapp_api/urls.py
"""

from django.urls import path, re_path
from myapp_api import views

urlpatterns = [
    re_path('^api/user/$', views.UserView.as_view()),
    re_path('^api/user/(?P<pk>\d+)/$', views.UserView.as_view()),
]
```

## 使用 Serializer 创建用户

接口地址

```python
/myapp_api/api/user/
```

### 定义视图：增加 post 方法接收数据

```python
"""
myapp_api/views.py
"""

from .serializers import UserSerializer
from myapp_api.models import User
from rest_framework.response import Response
from rest_framework.views import APIView

class UserView(APIView):
		def get (self, request, pk=None):
		"""
		省略。。。
		"""
    def post(self, request):
        # 调用序列化器将提交的数据进行反序列化
        user_ser = UserSerializer(data=request.data)
        # 获取反序列化是否通过
        if user_ser.is_valid():
            # 保存到数据库
            user_ser.save()
            msg = '创建用户成功'
            code = 200
        else:
            msg = '创建用户失败，请检查数据格式'
            code = 400
        reslut = {'code': code, 'msg': msg}
        return Response(reslut)
```

### Serializer 定义 create() 方法

```python
"""
myapp_api/serializers.py
"""

from myapp_api.models import User
from rest_framework import serializers

class UserSerializer(serializers.Serializer):

    # 字段与使用的模型字段须相对应
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=30)
    city = serializers.CharField(max_length=30)
    sex = serializers.CharField(max_length=10)
    age = serializers.IntegerField()

		# validated_data 是提交的 json 数据
    def create(self, validated_data):
        return User.objects.create(**validated_data)
```

## 使用 Serializer 更新用户

接口地址：

```python
/myapp_api/api/user/2
```

### 定义视图：增加 put 方法接收数据

```python
"""
myapp_api/views.py
"""

from .serializers import UserSerializer
from myapp_api.models import User
from rest_framework.response import Response
from rest_framework.views import APIView

class UserView(APIView):
		def get (self, request, pk=None):
		"""
		省略。。。
		"""
    def post(self, request):
		"""
		省略。。。
		"""
		def put(self, request, pk=None):
		        user_obj = User.objects.get(id=pk)
		        # 调用序列化器，传入已有对象和提交的数据
		        user_obj = UserSerializer(instance=user_obj, data=request.data)
		        if user_obj.is_valid():
		            user_obj.save()
		            msg = '更新用户成功'
		            code = 200
		        else:
		            msg = '更新用户失败，请检查数据格式'
		            code = 400
		        result = {'oode': code, 'msg': msg}
		        return Response(request)
```

### Serializer 定义 update() 方法

```python
"""
myapp_api/serializers.py
"""

from myapp_api.models import User
from rest_framework import serializers

class UserSerializer(serializers.Serializer):

    # 字段与使用的模型字段须相对应
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=30)
    city = serializers.CharField(max_length=30)
    sex = serializers.CharField(max_length=10)
    age = serializers.IntegerField()

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name")
        instance.city = validated_data.get("city")
        instance.sex = validated_data.get("sex")
        instance.age = validated_data.get("age")
        instance.save()
        return instance
```

## 使用 Serializer 删除用户

接口地址：

```python
/myapp_api/api/user/2
```

```python
"""
myapp_api/views.py
"""

from .serializers import UserSerializer
from myapp_api.models import User
from rest_framework.response import Response
from rest_framework.views import APIView

class UserView(APIView):
		def get (self, request, pk=None):
		"""
		省略。。。
		"""
    def post(self, request):
		"""
		省略。。。
		"""
		def put(self, request, pk=None):
		"""
		省略。。。
		"""
		def delete(self, request, pk=None):
		        user_obj = User.objects.get(id=pk)
		        try:
		            # 直接通过 model 删除，无需序列化器
		            user_obj.delete()
		            msg = '用户删除成功'
		            code = 200
		        except Exception as e:
		            msg = '用户删除失败 %s' %e
		            code = 400
		        result = {'code': code, 'msg': msg}
		        return Response(result)
```