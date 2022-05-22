# DRF 序列化器

## 序列化与反序列化

### JSON 序列化

```python
import json
# 序列化
computer = {"主机":5000,"显示器":1000,"鼠标":60,"键盘":150}

json.dumps(computer)

# 反序列化
json.loads(json_obj)
```

### Django 内置 Serializers 模块

Serializers 是 Django 内置的一个序列化器，可直接将 Python 对象转为 JSON 格式，但不支
持反序列化

```python
from django.core import serializers

obj = User.objects.all()

data = serializers.serialize('json', obj)
```

### Django 内置 JsonResponse 模块

JsonResponse 模块自动将 Python 对象转为 JSON 对象并响应

# DRF 序列化器

DRF 中有一个 serializers 模块专门负责数据序列化，DRF 提供了更先进、更高级别的序列化方案

### 序列化器支持三种类型

"""
myapp_api/serializers.py
"""

1. **Serializer** ：对Model（数据模型）进行序列化，需自定义字段映射
2. **ModelSerializer** ：对Model进行序列化，会自动生成字段和验证规则，默认还包含简单的create()和update()方法
3. **HyperlinkedModelSerializer** ：与ModelSerializer类似，只不过使用超链接来表示关系而不是主键ID

## Serializer

[使用 Serializer 操作数据](./%E4%BD%BF%E7%94%A8%20Serializer%20%E6%93%8D%E4%BD%9C%E6%95%B0%E6%8D%AE.md)

### 序列化器工作流程

1. **序列化（读数据）**

视图里通过 ORM 从数据库获取数据查询集对象 → 数据传入序列化器 → 序列化器将数据进行序列化 → 调用序列化器的.data获取数据 → 响应返回前端

1. **反序列化（写数据）**

视图获取前端提交的数据 → 数据传入序列化器 → 调用序列化器的.is_valid方法进行效验 → 调用序列化器的.save()方法保存数据

### 序列化器常用方法与属性

1. serializer.is_valid()

调用序列化器验证是否通过，传入 raise_exception=True 可以在验证失败时由 DRF 响应 400 异常

1. serializer.errors()

获取反序列化器验证的错误信息

1. serializer.data()

获取序列化器返回的数据

1. serializer.save()

将验证通过的数据保存到数据库（ORM操作）

### 序列化器参数

**常用参数**

| 名称 | 作用 |
| --- | --- |
| max_length | 最大长度 |
| min_length | 最小长度 |
| allow_blank | 是否允许为空 |
| trim_whitespace | 是否截断空白字符 |
| max_value | 最大值，适用于数值 |
| min_value | 最小值，适用于数值 |


**通用参数**

| 名称 | 作用 |
| --- | --- |
| read_only | 说明该字段仅用于序列化，默认False，若设置为True，反序列化可不传 |
| write_only | 该字段仅用于反序列化，默认False |
| required | 该字段在反序列化时必须输入，默认True |
| default | 反序列化时使用的默认值 |
| allow_null | 是否允许为NULL，默认False |
| validators | 指定自定义的验证器 |
| error_message | 包含错误编号与错误信息的字典 |

```python
name = serializers.CharField(max_length=30,
                            error_messages={ # 设置每种错误的提示
                                "blank": "请输入姓名",
                                "required": "该字符必填",
                                "max_lenth": "字符长度"
                            })
```

### 拓展验证规则

**如果常用参数无法满足验证要求时，可通过钩子方法扩展验证规则**

局部钩子：validate_字段名(self, 字段值)

全局钩子：validate(self, 所有校验的数据字段)

```python
"""
myapp_api/serializers.py
"""

# 局部钩子
# 姓名不能包含数字
def validate_name(self, attrs): # attrs 是该字段的数值
    from re import findall
    if findall('\d+', attrs):
        raise serializers.ValidationError("姓名不能包含数字")
    else:
        return attrs

# 全局钩子
def validate(self, attrs):  # attrs 是所有字段组成的字典
    sex = attrs.get('sex')
    if sex != "男" and sex != "女":
        raise serializers.ValidationError("性别只能选择男或者女？")
    else:
        return attrs
```

**如果钩子无法满足需要，可以自定义验证器，更灵活**

在序列化类外面定义验证器，使用validators参数指定验证器

```python
"""
myapp_api/serializers.py
"""

class UserSerializer(serializers.Serializer):

    # 自定义验证器
    def check_name(data):
        if data.startswitch('x'):
            raise serializers.ValidationError('姓名不能以 x 开头!')
        else:
            return data

    # 字段与使用的模型字段须相对应
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=30,
                                 validators=[check_name],   # 调用自定义验证器
                                 error_messages={           # 添加每种错误提示
                                     "blank": "请输入姓名",
                                     "required": "该字符必填",
                                     "max_lenth": "字符长度"
                                 })
```

## ModelSerializer

ModelSerializer 类型不需要自定义字段映射和定义create、update方法，使用起来方便很多

```python
"""
myapp_api/serializers.py
"""

from myapp_api.models import User
from rest_framework import serializers

class UserSerializer(serializers.Serializer):
    class Meta:
        model = User    # 指定数据模型
        fields = '__all__'  # 显示所有字段
```

**Meta 类常用属性**

| fields | 显示所有或指定字段 |
| --- | --- |
| exclude | 排除某个字段，元组格式，不能与fields同时用 |
| read_only_fields | 只读字段，即只用于序列化，不支持修改 |
| extra_kwargs | 添加或修改原有的字段参数，字典格式 |
| depth | 根据关联的数据递归显示，一般是多表 |

```python
"""
myapp_api/serializers.py
"""

from myapp_api.models import User
from rest_framework import serializers

class UserSerializer(serializers.Serializer):
    class Meta:
        model = User    # 指定数据模型
        fields = '__all__'  # 显示所有字段

        read_only_fields = ('id', )

        extra_kwargs = {
            'name': {'max_length': 10, 'required': True},
            'city': {'max_length': 10, 'required': True},
            'sex': {'max_length': 10, 'required': True},
            'age': {'max_length': 10, 'max_value': 100, 'required': True},
        }
```

## HyperModelSerializer

与MedelSerializer使用方法一样。只不过它使用超链接来表示关系而不是主键ID

```python
"""
myapp_api/serializers.py
"""

from myapp_api.models import User
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User    # 指定数据模型
        fields = "__all__"  # 显示所有字段
```

```python
"""
myapp_api/urls.py
"""

from django.urls import re_path
from myapp_api import views

urlpatterns = [
    re_path('^api/user/$', views.UserView.as_view(), name="user-detail"),
    re_path('^api/user/(?P<pk>\d+)/$', views.UserView.as_view(), name="user-detail"),
]
```

```python
"""
myapp_api/views.py
"""

# 更改视图
user_ser = UserSerializer(user_obj, context={'request': request}) 

```

```python
# 更改路由
re_path('^api/user/$', views.UserView.as_view(), name="user-detail"),
re_path('^api/user/(?P<pk>\d+)/$', views.UserView.as_view(), name="user-detail"),
```

## 关联表显示

## SerializerMethodField

DRF序列化器默认仅返回数据模型中已存在资源，如果想新增返回字段或者二次处理，该
如何操作呢？

示例：给项目API增加一个字段，这个字段数据可从别的表中获取

```python
"""
myapp_api/serializers.py
"""

from myapp_api.models import User
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    app_count = serializers.SerializerMethodField()

    class Meta:
        model = User    # 指定数据模型
        fields = "__all__"  # 显示所有字段

    # get_字段名
    def get_app_count(self, obj):
        return len(obj.app_set.all())
```

## 改变序列化和反序列化的行为

可以通过重写下面两个方法改变序列化和反序列化的行为

- to_internal_value()

处理反序列化的输入数据，自动转换Python对象，方便处理

- to_representation()

处理序列化数据的输出

如果提交API的数据与序列化器要求的格式不符合，序列化器就会出现错误。这时就可以重写to_internal_value()方法只提取出我们需要的数据

```json
/*提交的数据*/

{
	"project_data": {
		"name": "测试",
		"describe": "测试。。",
	},
	"extra_info": {
		"msg": "hello world"
	}
}
```

```python
"""
重写的方法
"""

def to_internal_value(self, data):
		# data 是未验证的数据
		# 提取数据
		project_data = data['project_data']
		return super().to_internal_value(project_data)
```

希望给返回的数据添加一个统计应用数量的字段

```python
def to_representation(self, instance):
    # 调用父类获取当前序列化数据， instance 代表每个对象实例
    data = super().to_representation(instance)
    data["app_count"] = len(instance.app_set.all())
    return  data
```
