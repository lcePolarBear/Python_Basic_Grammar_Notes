# 多表操作：一对一
## 创建模型关系
- 向模型类添加模型
    ```python
    # models.py
    from django.db import models

    # 原有的用户表，作为父表
    class User(models.Model):
        user = models.CharField(max_length=30, verbose_name="用户名")
        name = models.CharField(max_length=30, verbose_name="姓名")
        sex = models.CharField(max_length=10, verbose_name="性别")
        age = models.IntegerField(verbose_name="年龄")
        label = models.CharField(max_length=100, verbose_name="标签")

        class Meta:
            db_table = "user"
            verbose_name = "用户表"
            verbose_name_plural = "用户表"
            ordering = ['id']

        def __str__(self):
            return self.name

    # 新创建一个身份证表，用于和用户表一对一对应，作为子表
    class IdCord(models.Model):
        number = models.CharField(max_length=18, verbose_name="身份证号")
        address = models.CharField(max_length=50, verbose_name="家庭地址", default="beijing")
        # 定义一对一的关系，并且必须添加 on_delete 删除关系
        user = models.OneToOneField(User, on_delete=models.CASCADE)

        class Meta:
            db_table = "id"
            verbose_name = "身份证表"
            verbose_name_plural = "身份证表"
            ordering = ["id"]

        def __str__(self):
            return self.number
    ```
- 向后台注册模型类
    ```python
    # myapp/admin.py
    from django.contrib import admin
    from myapp import models

    admin.site.register(models.User)
    admin.site.register(models.IdCord)
    ```
- 生成迁移文件并同步数据库
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```
## 一对一增删改查
### 增
- 同步增
    ```python
    # views.py
    from django.http import HttpResponse
    from myapp.models import User,IdCord

    def data_create(request):
        user_obj = User.objects.create(
            user="112",
            name="kun",
            sex="man",
            age=24,
            label="devops"
        )
        IdCord.objects.create(
            user = user_obj,
            number="123456789",
        )
        return HttpResponse("新增成功！")
    ```
- 向已有用户添加身份证信息
    ```python
    # views.py
    from django.http import HttpResponse
    from myapp.models import User,IdCord

    def data_create(request):
        user_obj = User.objects.get(user="chen")
        id_obj = IdCord.objects.create(
            user = user_obj,
            number="123456789",
        )
        return HttpResponse("新增成功！")
    ```
### 删
- 由于两表之间存在 on_detele 关联，删除 User 数据时 IdCard 会同步删除对应数据
    ```python
    # views.py
    from django.http import HttpResponse
    from myapp.models import User,IdCord

    def data_delete(request):
        User.objects.filter(user="chen").delete()
        return HttpResponse("删除成功！")
    ```
### 改
- 通过 User 用户的对象修改 IdCard 信息
```python
    # views.py
    from django.http import HttpResponse
    from myapp.models import User,IdCord

    def data_update(request):
        user_obj = User.objects.get(user="chen")
        # 修改 IdCard 信息
        user_obj.idcord.address = "shanghai"
        # 修改 User 表信息
        user_obj.age = 25
        # 保存 IdCard 信息
        user_obj.idcord.save()
        # 保存 User 表信息
        user_obj.save()
        return HttpResponse("修改完成！")
```
### 查

- 正向查询：从 IdCard 查 User
    ```python
    # views.py
    from django.http import HttpResponse
    from myapp.models import User,IdCord

    def data_select(request):
        user_obj = User.objects.get(user="chen")
        return HttpResponse(user_obj.idcord.number)
    ```
- 反向查询：从 User 查 IdCard
    ```python
    # views.py
    from django.http import HttpResponse
    from myapp.models import User,IdCord

    def data_select(request):
        id_obj = IdCord.objects.get(user="2")
        return HttpResponse(id_obj.user.user)

# 多表操作：一对多
- A 表中的某个记录对应 B 表中的多条记录，使用 ForeignKey 建立关系
- 例如：一个项目有多个应用，一个应用只能属于一个项目

## 创建模型关系
- 向模型类添加模型
    ```python
    # models.py
    from django.db import models

    class Projects(models.Model):
        name = models.CharField(max_length=30,verbose_name="项目名")
        desc = models.CharField(max_length=30, null=True, verbose_name="项目描述")
        datatime = models.DateTimeField(auto_now_add=True,verbose_name="创建日期")

        def __str__(self):
            return self.name

        class Meta:
            db_table = 'project'
            verbose_name_plural = '项目'

    class Apps(models.Model):
        name = models.CharField(max_length=30,verbose_name="应用名")
        desc = models.CharField(max_length=30, null=True, verbose_name="应用描述")
        datatime = models.DateTimeField(auto_now_add=True, verbose_name="创建日期")
        # 定义一对多模型关系
        project = models.ForeignKey(Projects, on_delete=models.CASCADE)

        def __str__(self):
            return self.name

        class Meta:
            db_table = 'app'
            verbose_name_plural = '应用'
    ```
- 向后台注册模型类
    ```python
    # myapp/admin.py
    from django.contrib import admin
    from myapp import models

    admin.site.register(models.Projects)
    admin.site.register(models.Apps)
    ```
- 生成迁移文件并同步数据库
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

## 一对多增删改查
### 增
- 增数据的方式与 一对一 类似
    ```python
    # views.py
    from django.http import HttpResponse
    from myapp.models import Projects,Apps

    # 创建一个新的项目
    def Project_create(request):
        Projects.objects.create(name="电商项目",desc="电商真牛B")
        return HttpResponse("项目新增完成")

    # 创建一个新的应用并于项目对应
    def App_create(request):
        projects_obj = Projects.objects.get(name="电商项目")
        apps_obj = Apps.objects.create(
            name="购物车",
            desc="购物车模块",
            project=projects_obj
        )
        return  HttpResponse("购物车模块增加完成")
    ```
### 删和改可以参考 一对一 的代码逻辑
### 查
- 查询某个应用所属项目
    ```python
    # views.py
    def Project_select(request):
        app = Apps.objects.get(name="购物车")
        return HttpResponse(app.project.name)
    ```
- 查询所有应用应属项目
    ```python
    # views.py
    def Project_select(request):
        app = Apps.objects.all()
        return render(request,"index.html",{'app':app})
    ```
    ```html
    <!--index.html-->
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Title</title>
    </head>
    <body>
    {% for foo in app %}
        <p>{{ foo.name }}:{{ foo.project.name }}</p>
    {% endfor %}
    </body>
    </html>
    ```
- 查询某个项目有哪些应用
    ```python
    # views.py
    def Project_select(request):
        project = Projects.objects.get(name="电商项目")
        return HttpResponse(project.apps_set.all())
    ```
- 查询所有项目有哪些引用
    ```python
    # views.py
    def Project_select(request):
        project = Projects.objects.all()
        return render(request,"index.html",{"project":project})
    ```
    ```html
    <!--index.html-->
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Title</title>
    </head>
    <body>
    {% for foo in project %}
        <p>{{ foo }}</p>
        {% for i in foo.apps_set.all %}
        <p>{{ i }}</p>
        {% endfor %}
    {% endfor %}
    </body>
    </html>
    ```

## 案例：使用表单完成 app 的添加
```python
# views.py
def deploy_app(request):
    # 用于处理 POST 请求
    if request.method == "POST":
        # 从表单获取录入的 app_name 信息
        app_name = request.POST.get("app_name")
        # 从表单获取录入的 app_desc 信息
        app_desc = request.POST.get("app_desc")
        # 从表单获取录入的 project_name 信息
        project_name = request.POST.get("project_name")
        # 通过 project_name 获取 project 对象
        project = Projects.objects.get(name=project_name)
        # 增加 app 数据，并关联指定的 project
        Apps.objects.create(
            name = app_name,
            desc = app_desc,
            project = project
        )
        return HttpResponse("增加成功！")
    # 用于处理 GET 请求
    else:
        project_list = Projects.objects.all()
        return render(request,"index.html",{'project_list':project_list})
```
```html
<!--index.html-->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
<form action="/index/" method="post">
    app 名称：<input type="text" name="app_name">
    app 描述：<input type="text" name="app_desc">
    <select name="project_name" id="">
        {% for project in project_list %}
            <option value="{{ project.name }}">{{ project.name }}</option>
        {% endfor %}
    </select>
    <input type="submit" value="提交">
</form>
</body>
</html>
```

# 多表操作：多对多
- 使用 ManyToManyField 建立关系
- 例如：一个应用部署到多台服务器，一个服务器部署多个应用

## 创建模型关系
> Django会自动创建一个表来管理多对多关系，称为 __中间表__ ；这个中间表的名称使用多对多的名称和包含这张表的模型的名称生成，也可以使用 db_table 选项指定这个中间表名称
- 向模型类添加 server 模型
    ```python
    # views.py
    class Server(models.Model):
        hostname = models.CharField(max_length=30,verbose_name="主机名")
        ip = models.GenericIPAddressField(null=True,verbose_name="ip 地址")
        desc = models.CharField(max_length=30,null=True,verbose_name="主机描述")
        app = models.ManyToManyField(Apps)

        def __str__(self):
            return self.hostname

        class Meta:
            db_table = "Server"
            verbose_name_plural = "服务器"
    ```
- 向后台注册模型类
    ```python
    # myapp/admin.py
    from django.contrib import admin
    from myapp import models

    admin.site.register(models.Projects)
    admin.site.register(models.Server)
    admin.site.register(models.Apps)
    ```
- 生成迁移文件并同步数据库
    ```bash
    python manage.py makemigrations
    python manage.py migrate

## 多对多增删改查
### 增
- 创建一个应用数据并联系到到指定服务器数据
    ```python
    # views.py
    def App_create(request):
        projects_obj = Projects.objects.get(name="在线教育项目")
        apps_obj = Apps.objects.create(
            name="直播",
            desc="直播模块",
            project=projects_obj
        )
        server = Server.objects.get(hostname="server_1")
        server.app.add(apps_obj)
        return  HttpResponse("应用增加完成")
    ```
- 对中间表进行增操作
    ```python
    # 获取已有的服务器
    server = Server.objects.get(hostname="server_1")
    # 将应用 id3 关联该服务器
    server.app.add(3)
    # 将应用 id3,4,5 关联该服务器
    server.app.add(3,4,5)
    ```
### 删
- 取消多表之间的中间表的连接关系之后才能对表数据进行删除
- 删除中间表连接关系
    ```python
    # views.py
    def server_app_delete(request):
        server = Server.objects.get(hostname="server_2")
        app = Apps.objects.get(name="hadoop")
        # 操作 app 对象 (id) 进行删除
        server.app.remove(app)
        return HttpResponse("删除完成")
    ```
- 使用 一对一 表关系的删除方法对表数据进行删除（因为数据在两表之间的连接关系被解除了）
- 将指定服务器关联的所有应用取消关联
    ```python
    # views.py
    def server_app_delete(request):
        server = Server.objects.get(hostname="server_2")
        server.app.clear()
        return HttpResponse("删除完成")
    ```
### 改
- 多对多的关系一般不用于中间表，基础表的更新可以参照一对一表更新
### 查
- 获取某台服务器部署的应用
    ```python
    # views.py
    def server(request):
        server_list = Server.objects.get(hostname="server_1")
        return HttpResponse(server_list.app.all())
    ```
- 获取所有服务器部署的应用
    ```python
    # views.py
    def server(request):
        server_list = Server.objects.all()
        return render(request, "index.html", {"server_list": server_list})
    ```
    ```html
    <!--index.html-->
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Title</title>
    </head>
    <body>
    {% for server in server_list %}
        {% for foo in server.app.all %}
            {{ server }}:{{ foo }}<br>
        {% endfor %}
    {% endfor %}
    </body>
    </html>
    ```
- 查询某个应用部署到哪些服务器
    ```python
    # views.py
    def server(request):
        app = Apps.objects.get(name="购物车")
        return HttpResponse(app.server_set.all())
    ```
- 查询所有应用对应部署的服务器
    ```python
    # views.py
    def server(request):
        app = Apps.objects.all()
        return render(request,"index.html",{'app_list':app})
    ```
    ```html
    <!--index.html-->
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Title</title>
    </head>
    <body>
    {% for app in app_list %}
        {% for server in app.server_set.all %}
            {{ app }}:{{ server }}<br>
        {% endfor %}
    {% endfor %}
    </body>
    </html>
    ```

## 案例：显示所有 app 对应的项目及其所在的服务器
```python
# views.py
def deploy_app(request):
    app_list = Apps.objects.all()
    return render(request,"index.html",{'app_list':app_list})
```
```html
<!--index.html-->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
<table border="1">
    <thead>
        <tr>
            <th>应用名称</th>
            <th>项目名称</th>
            <th>服务器名称</th>
        </tr>
    </thead>
    <tbody>
    {% for app in app_list %}
        <tr>
            <td>{{ app.name }}</td>
            <td>{{ app.project.name }}</td>
            <td>
                {% for server in app.server_set.all %}
                    {{ server }}
                {% endfor %}
            </td>
        </tr>
    {% endfor %}
    </tbody>
</table>
</form>
</body>
</html>
```