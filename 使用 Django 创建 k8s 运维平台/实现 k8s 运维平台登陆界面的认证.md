# 实现 k8s 运维平台登陆界面的认证

### 准备登陆界面

login.html

创建登录功能应用
python manage.py startapp dasboard

使用 session 则必须启用数据库，用于保存 session 状态

python manage.py makemigrations
python manage.py migrate

### 创建 User 表用于存储 kubeconfig 文件登录信息，并通过随机数生成 token 记录会话信息。token 既可以用于表示登录信息也可以用于记录会话信息
from django.db import models

class User(models.Model):
    auth_type = models.CharField(max_length=30)
    token = models.CharField(max_length=100)    # 标识用户
    content = models.CharField(max_length=100)
    datetime = models.DateTimeField(auto_now=True)

### 使用 k8s 连接成功与否判断登录凭据是否有效
```python
from kubernetes import client, config
from dashboard.models import User
import yaml

def auth_check(auth_type, token):
    if auth_type == "token":
        # 验证 token 是否有效，有效则跳转到首页
        configuration = client.Configuration()
        configuration.host = "https://192.168.102.249:16443"
        # ca_file = os.path.join(os.getcwd(), "ca.crt")
        # configuration.ssl_ca_cert = ca_file
        # 禁用证书验证
        configuration.verify_ssl = False
        configuration.api_key = {"authorization": "Bearer " + token}
        client.Configuration.set_default(configuration)
        try:
            apps_api = client.CoreApi()
            apps_api.get_api_versions()
            return True
        except Exception as e:
            print(e)
            return False
    elif auth_type == "kubeconfig":
        try:
            user = User.objects.filter(token = token)
            # 提取 kubeconfig 文件内容
            content = user[0].content
            # 转化为 yaml 文件
            yaml_content = yaml.load(content, Loader=yaml.FullLoader)
            # 加载 kubeconfig yaml 文件
            config.load_kube_config_from_dict(yaml_content)
            core_api = client.CoreApi()
            core_api.get_api_versions()
            return True
        except Exception as e:
            print(e)
            return False
```
### 登录接口逻辑
```python
from django.shortcuts import render
from django.http import JsonResponse
from devops import k8s
import random
import hashlib
from dashboard.models import User


def login(request):
    if request.method == "GET":
        return render(request, "login.html")
    elif request.method == "POST":
        # 处理 token
        token = request.POST.get("token")
        if token:
            if k8s.auth_check("token", token):
                # 标识用户登录
                request.session['is_login'] = True
                # 标识登陆类型
                request.session['auth_type'] = "token"
                # 用 token 来标识用户
                request.session['token'] = token
                code = 0
                msg = "success!"
            else:
                code = 1
                msg = "faild!"
        else:
            # 处理 kubeconfig
            file_obj = request.FILES.get("file")
            # 生成一个随机字符串（token）保存到 session 中用于 kubeconfig 登录标识用户
            token_rander = hashlib.md5(str(random.random()).encode()).hexdigest()
            try:
                content = file_obj.read().decode() # bytes to str
                User.objects.create(
                    auth_type="kubeconfig",
                    token = token_rander,
                    content = content
                )
            except Exception as e:
                code = 1
                msg = "faild!"
            if k8s.auth_check("kubeconfig", token_rander):
                request.session['is_login'] = True
                request.session['auth_type'] = "kubeconfig"
                request.session['token'] = token_rander

                code = 0
                msg = "success!"
            else:
                code = 1
                msg = "faild!"

        result = {'code': code, 'msg': msg}
        return JsonResponse(result)
```
### 应用登陆限制装饰器
```python
from django.shortcuts import redirect


def self_login_required(func):
    def inner(request, *args, **kwargs):
        is_login = request.session.get('is_login', False)
        if is_login:
            return func(request, *args, **kwargs)
        else:
            return redirect("/login")
    return inner
```
```python
@k8s.self_login_required
def index(request):
    return render(request, "index.html")
```
### 注销登录
```python
# dashboard/views.py
def logout(request):
    # 针对使用 kubeconfig 文件进行登陆的用户需要在注销时将 kubeconfig 信息删除
    var search_key = $('input[name="name"]').val()
    request.session.flush()
    return redirect(login)
```