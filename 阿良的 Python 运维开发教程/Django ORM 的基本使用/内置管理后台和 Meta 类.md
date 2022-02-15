# 内置管理后台和 Meta 类
- 内置后台用于为管理员提供更简单的数据库操作方式
## 激活管理后台
- 创建管理后台访问 url （创建 django 项目时默认创建）
    ```python
    # urls.py
    from django.contrib import admin
    from django.urls import path

    urlpatterns = [
        path('admin/', admin.site.urls),
    ]
    ```
- 创建后台管理员账号
    ```bash
    python manage.py createsuperuser
    ```
- 注册模型
    ```python
    # mmyapp/admin.py
    from django.contrib import admin
    from myapp import models

    # Register your models here.
    admin.site.register(models.User)
    ```
- 设置语言和时区
    ```python
    # settings.py
    LANGUAGE_CODE = 'zh-hans'

    TIME_ZONE = 'Asia/Shanghai'

    USE_I18N = True

    USE_L10N = True

    USE_TZ = False
    ```
## Model 模型中的 Meta 类与方法
- Meta 类用于定义一些 Django 模型类的行为特性
- 示例
    ```python
    # models.py
    from django.db import models

    class User(models.Model):
        user = models.CharField(max_length=30)
        name = models.CharField(max_length=30)
        sex = models.CharField(max_length=10)
        age = models.IntegerField()
        label = models.CharField(max_length=100)

        class Meta:
            # 指定APP名称，当模型类不在默认 APP 的 models.py 文件中，需要指定模型类是属于哪个APP
            app_label = "myapp"
            # 指定生成的数据库表名称，默认是“应用名_模型名”
            db_table = "myapp_user"
            # 对象的可读名称（带 s）
            verbose_name = "用户表"
            # 名称复数形式（不带 s）
            verbose_name_plural = "用户表"
            # 对象的默认顺序，个字符串表示字段名，元素前面带减号表示倒序，没有表示升序，问号表示随机排序
            ordering = ["id"]
        def __str__(self):
            # 返回字段值
            return self.name
    ```