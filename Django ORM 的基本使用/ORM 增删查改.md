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
- 使用 MySQL 工具端查看生成的数据表
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