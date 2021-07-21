# Session 和 Cookie 基础知识

## Cookie 工作方式
- 浏览器第一次访问服务器时，服务器此时肯定不知道它的身份，所以创建一个独特的身份标识数据，格式为 key=value ，放入到 Set-Cookie 字段里，随着响应报文发给浏览器
- 浏览器看到有 Set-Cookie 字段以后就知道这是服务器给的身份标识，于是就保存起来，下次请求时会自动将此 key=value 值放入到 Cookie 字段中发给服务器
- 服务器收到请求报文后，发现 Cookie 字段中有值，就能根据此值识别用户的身份然后提供个性化的服务
### Cookie
- 数据存储在浏览器端
- 方便与 JS 交换数据
- 方便获取用户信息
- 存在拦截和泄露 Cookie 的风险

## Session 工作方式
- 试想一下，如果将用户账户的一些信息都存入 Cookie 中的话，一旦信息被拦截，那么所有的账户信息都会可能被泄露丢，这是不安全的
- 在一次会话中将重要信息保存在Session中，浏览器只记录SessionId一个SessionId对应一次会话请求
### Seesion
- 数据存储在服务端
- 高效、安全、不依赖浏览器环境
- 服务器端会为每个用户分配一个 ID 标识

## Django 启用 Session
```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    # 默认启用 session
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'myapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 默认启用 session
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```
- Django 默认启用 Session ，所以在内置登录认证模块在登陆后会在 django_session 表生成 session 数据