# DRF 视图

在DRF框架中提供了众多的通用视图基类与扩展类，以简化视图的编写

| 视图 |  说明 |
| --- | --- |
| View | Django默认的视图基类，负责将视图连接到URL，HTTP请求方法的基本调度，之前写类视图一般都用这个 |
| APIView | DRF提供的所有视图的基类，继承View并扩展，具备了身份认证、权限检查、流量控制等功能 |
| GenericAPIView | 对APIView更高层次的封装，例如增加分页、过滤器 |
| GenericViewSet | 继承 GenericAPIView 和 ViewSet |
| ViewSet | 继承 APIView ，并结合 router 自动映射路由 |
| ModelViewSet | 继承 GenericAPIView 和五个扩展类，封装好各种请求，更加完善，业务逻辑基本不用自己写了 |

## APIView 类

DRF提供的所有视图的基类，继承View并扩展，具备了身份认证、权限检查、流量控制等功能

```python
"""
my_app/views.py
"""

from rest_framework.views import APIView

class UserView(APIView):
    def get (self, request, pk=None):
        """
        """
        return Response(result)
    def post(self, request):
        """
        """
    def put(self, request, pk=None):
        """
        """
    def delete(self, request, pk=None):
        """
        """
```

## Request 与 Response

DRF 传入视图的 request 对象不再是 Django 默认的 HttpRequest 对象，而是基于 HttpRequest 类扩展后的 Request 类的对象

Request 对象的数据是自动根据前端发送的数据统一解析数据格式

**常用属性**

- request.data

返回POST提交的数据，与request.POST类似

- request.query_params

返回 GET URL 参数，与 request.GET 类似

DR F提供了一个响应类 Reponse ，响应的数据会自动转换符合前端的 JSON 数据格式

**导入**

```python
from rest_framework.response import Response
```

**格式**

```python
Response(data,  # 响应序列化处理后的数据，传递python对象
         status=None,   # 状态码，默认200
         template_name=None,    # 模板名称
         headers=None,  # 用于响应头信息的字典
         content_type=None) # 响应数据的类型
```

**使用方法**

```python
return Reponse(data=data, status=status.HTTP_404_NOT_FOUND)
```

为了方便设置状态码，rest_framework.status模块提供了所有HTTP状态码，以下是一些常用的

| 状态码 |  说明 |
| --- | --- |
| HTTP_200_OK | 请求成功 |
| HTTP_301_MOVED_PERMANENTLY | 永久重定向 |
| HTTP_302_FOUND | 临时重定向 |
| HTTP_304_NOT_MODIFIED | 请求的资源未修改 |
| HTTP_403_FORBIDDEN | 没有权限访问 |
| HTTP_404_NOT_FOUND | 页面没有发现 |
| HTTP_500_INTERNAL_SERVER_ERROR | 服务器内部错误 |
| HTTP_502_BAD_GATEWAY | 网关错误 |
| HTTP_503_SERVICE_UNAVAILABLE | 服务器不可达 |
| HTTP_504_GATEWAY_TIMEOUT | 网关超时 |

## GenericAPIView类

GenericAPIView 对 APIView 更高层次的封装，实现以下功能

- 增加 queryset 属性，指定操作的数据，不用再将数据传给序列化器，会自动实现
- 增加 serializer_class 属性，直接指定使用的序列化器
- 增加过滤器属性：filter_backends
- 增加分页属性：pagination_class
- 增加 lookup_field 属性和实现 get_object() 方法：用于获取单条数据，可自定义默认分组名（pk）

```python

```

## ViewSet 类

GenericAPIView 已经完成了许多功能，但会有一个问题，获取所有用户列表和单个用户需要分别定义两个视图和 URL 路由，使用 ViewSet 可以很好解决这个问题，并且实现了路由自动映射

ViewSet 视图集不再实现 get()、post() 等方法，而是实现以下请求方法动作

| 方法 |  说明 |
| --- | --- |
| list() | 获取所有数据 |
| retrieve() | 获取单个数据 |
| create() | 创建数据 |
| update() | 更新数据 |
| destory() | 删除数据 |

```python
# URL 路由

```

```python
# 视图
```

在路由这块定义与之前方式一样，每个 API 接口都要写一条 URL 路由，但实际上我们用 ViewSet 后，就不用自己设计 URL 路由及绑定 HTTP 方法了，会自动处理 URL 路由映射

```python
# 路由

```

## ModelViewSet 类

ModelViewSet 继承 GenericAPIView 和五个扩展类，封装好各种请求，更加完善，业务逻辑基本不用自己写了，只需要指定 serializer_class 和 queryset ，就可以直接进行增删改查

```python

```

| 动作 | 类名 | HTTP 方法 | 说明 | URL 示例 |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |

由于 ModelViewSet 有较高的抽象，实现自动增删改查功能。对于增、改在很多场景无法满足需求，这就需要重写对应方法了

重写 create() 方法，修改数据和响应内容格式

```python
# 
```