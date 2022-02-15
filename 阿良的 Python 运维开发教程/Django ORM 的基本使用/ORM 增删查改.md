# 使用 ORM 实现 MySQL 数据库的增删改查
- ORM 将 Model Python 代码转化为 SQL 去操作数据库
## 将 Model 模型类映射到数据库中
- 使用模型类定义一个 User 表，包含多字段
    ```python
    # myapp/model.py
    from django.db import models

    class User(models.Model):
        user = models.CharField(max_length=30)
        name = models.CharField(max_length=30)
        sex = models.CharField(max_length=10)
        age = models.IntegerField()
        label = models.CharField(max_length=100)
    ```
- 向 INSTALLED_APPS 列表添加 APP 名称，并修改 django 默认连接数据库
    ```python
    # settings.py
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        # 在列表中添加上应用 myapp
        'myapp'
    ]

    ···
    # 重写数据库连接配置 MySQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'test',
            'USER': 'root',
            'PASSWORD': '123456',
            'HOST': '192.168.2.212',
            'PORT': '3306'
        }
    }
    ```
- 指定数据库驱动
    ```bash
    # 使用命令行 pip 安装 pymysql 模块
    pip install pymysql
    ```
    ```python
    # myapp/__init__.py
    import pymysql
    pymysql.install_as_MySQLdb()
    ```
- 将模型类生成具体的数据库表
    ```python
    # 生成迁移文件,迁移文件在 app 应用 migrations 路径下：0001_initial.py
    python manage.py makemigrations
    # 执行迁移文件生成表，生成的表不止包含有 User 表，还有 django 后台所需的表，即 INSTALLED_APPS 列表下所有的应用都会生成表
    python manage.py migrate
    ```
- 使用 MySQL 工具端查看生成的数据表，大部分生成的表为 Django 内置用户认证系统生成的表 [Django 用户认证系统]()
    - auth_group
    - auth_group_permissions
    - auth_permission
    - auth_user
    - auth_user_groups
    - auth_user_user_permissions
    - django_admin_log
    - django_content_type
    - django_migrations
    - django_session
    - myapp_user

## Model 模型类常用的字段
- 常用字段及其描述
    字段类型 | 描述
    ---- | ---
    AutoField(**options) | ID 自动递增，会自动添加到模型中
    BooleanField(**options) | 布尔值字段（true/false），默认值是 None
    CharField(max_length=None[,**options]) | 存储各种长度的字符串
    EmailField([max_length=254,**options]) | 邮件地址，会检查是否合法
    FileField([upload_to=None,max_length=100,**options]) | 保存上传文件， upload_to 是保存本地的目录路径
    FloatField([**options]) | 浮点数
    IntegerField([**options]) | 整数
    GenericIPAddressField(protocol=’both’, unpack_ipv4=False, **options) |  IP 地址
    TextField([**options]) | 大文本字符串
    URLField([max_length=200,**options]) | 字符串类型的 URL
    DateTimeField([auto_now=False,auto_now_add=False,**options]) | auto_now=True 时，第二次保存对象时自动设置为当前时间（一般用于最后一次修改的时间戳，比如更新）。auto_now_add=True 时，第一次创建时自动设置当前时间（一般用于创建时间的时间戳，比如新增）
    DateField([auto_now=False,auto_now_add=False,**options]) | 日期
    TimeField([auto_now=False,auto_now_add=False,**options]) | 时间
- 常用字段可配置的选项
    字段选项 | 描述
    ---- | ---
    null | 如果为 True ，字段用 NULL 当做空值，默认 False
    blank | 如果为 True ，允许为空，默认 False
    db_index | 如果为 True ，为此字段建立索引
    default | 设置字段的默认值
    primary_key | 如果为 True ，设置为主键
    unique | 如果为 True ，保持这个字段的值唯一
    verbose_name | 易读的名称，管理后台会以这个名称显示

## ORM 增删查改
- 在开始操作之前可以把 MySQL 的 general_log 开启，用以观察 ORM 执行的 sql 语句
### 增
```python
# 前端设置 urils 路由调用 views
# views.py
from django.http import HttpResponse
from myapp.models import User

def data_add(request):
    User.objects.create(
        user='chen',
        name='晨',
        sex='man',
        age=30,
        label="teacher,student"
    )
    return HttpResponse("用户添加成功")
```
或者
```python
from django.http import HttpResponse
from myapp.models import User

def data_add(request):
    Obj = User(
        user="kun",
        name="坤",
        sex="man",
        age=20,
        label="teacher,student"
    )
    Obj.save()
    return HttpResponse("用户添加成功")
```
### 删
```python
# views.py
from django.http import HttpResponse
from myapp.models import User

def data_delete(request):
    User.objects.filter(id=1).delete()
    return HttpResponse("id 为 1 的用户删除成功")
```
或者
```python
from django.http import HttpResponse
from myapp.models import User

def data_delete(request):
    obj = User.objects.get(id=1)
    obj.delete()
    return HttpResponse("id 为 1 的用户删除成功")
```
### 改
```python
# views.py
from django.http import HttpResponse
from myapp.models import User

def data_select(request):
    Obj = User.objects.filter(user="chen").update(age=27, label="运维开发")
    return HttpResponse("数据已更改")
```
或者
```python
# views.py
from django.http import HttpResponse
from myapp.models import User

def data_select(request):
    obj = User.objects.get(user='chen')
    obj.age = 25
    obj.label = "工程师"
    obj.save()
    return HttpResponse("数据已更改")
```
### 查
```python
# views.py
from django.shortcuts import render
from myapp.models import User

def data_select(request):
    # 获取所有数据
    Obj_all = User.objects.all()
    # 获取指定数据
    Obj_name = User.objects.filter(name="chen")
    # User 类不支持使用算术运算符，作比较需要使用指定函数
    Obj_age = User.objects.filter(age__gt=26)
    return render(request, "index.html", {'Obj': Obj,'Obj_name': Obj_name,'Obj_age': Obj_age})
```

## QuerySet 序列化
- ORM 查询返回的是 QuerySet 对象，我们可以使用序列化转换为 json
- 使用内建函数 serializers 完成转换
    ```python
    # views.py
    from django.http import HttpResponse
    from django.core import serializers
    from myapp.models import User

    def data_select(request):
        Obj = User.objects.all()
        data = serializers.serialize('json',Obj)
        return HttpResponse(data)
    ```
- 或者遍历 QuerySet 对象将字段拼接成字典，再通过 json 库编码
    ```python
    # views.py
    from django.http import HttpResponse
    from myapp.models import User
    import json

    def data_select(request):
        Obj = User.objects.all()
        d = {}
        for foo in Obj:
            d['user'] = foo.user
            d['name'] = foo.name
            d['sex'] = foo.sex
        data = json.dumps(d)
        return HttpResponse(data)
    ```