# DRF 常用功能

## 主流认证方式

- session
- token
- JWT

## DRF 认证

**DRF 支持四种认证方式**

| 认证方式 |  说明 |
| --- | --- |
| BasicAuthentication | 基于用户名和密码的认证，适用于测试 |
| SessionAuthentication | 基于 Session 的认证 |
| TokenAuthentication | 基于 Token 的认证 |
| RemoteUserAuthentication | 基于远程用户的认证 |

**DRF 支持权限**

| 权限 | 说明 |
| --- | --- |
| IsAuthenticated | 只有登录用户才能访问所有 API |
| AllowAny | 允许所有用户 |
| IsAdminUser | 仅管理员用户 |
| IsAuthenticatedOrReadOnly | 登录的用户可以读写 API ，未登录用户只读 |

### Session 认证

**所有视图（全局）启用认证**

```python
# DRF 配置

```

**视图级别启用认证**

```python

```

由于Django默认提供Session存储机制，可直接通过登录内置管理后台进行验证

当登录管理后台后，就有权限访问了

### Token 认证

1. 安装 APP

```python

```

1. 启用 Token 认证

```python

```

1. 生成数据库表

```python

```

1. 配置 Token 认证接口 URL

```python

```

使用用户名和密码登录测试，正常会返回 token 字符串

后面就可以直接 token 访问：把 token 字符串放到 header

默认的 obtain_auth_token 视图返回的数据是比较简单的，只有 token 一项，如果想返回更多的信息，
例如用户名，可以重写 ObtainAuthToken 类的方法实现

```python

```

## 限流

可以对接口访问的频率进行限制，以减轻服务器压力。应用场景：投票、购买数量等

```python

```

## 过滤

对于列表数据可能需要根据字段进行过滤，我们可以通过添加 django-fitlter 扩展来增强支持。

```python

```

在视图中指定过滤的字段

```python

```

## 搜索和排序

DRF提供过滤器帮助我们快速对字段进行搜索和排序

```python

```

## 分页

分页是数据表格必备的功能，可以在前端实现，也可以在后端实现，为了避免响应数据过大，造成前端压力，一般在后端实现

```python

```

默认分页器灵活度不高，例如不能动态传递每页条数，可以通过重写 PageNumberPagination 类属性改变默认配置

```python

```

DRF 配置指定模块路径

```python

```

默认返回的是一个固定格式 JSON 字符串，但这个格式与我们平时用的格式不太一样，所以希望把这个返回修改一下，可通过重写 PageNumberPagination 类实现

## 自动生成接口文档

Swagger来了，它是一个应用广泛的REST API文档自动生成工具，生成的文档可供前端人员查看

1. 安装

```python

```

1. 添加 app

```python

```

1. DRF 配置

```python

```

1. URl 路由

```python

```