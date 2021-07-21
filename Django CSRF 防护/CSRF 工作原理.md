# CSRF 工作原理
- CSRF（Cross Site Request Forgery）：跨站请求伪造，实现的原理是CSRF攻击者在用户已经登录目标网站之后，诱使用户访问一个攻击页面，利用目标网站对用户的信任，以用户身份在攻击页面对目标网站发起伪造用户操作的请求，达到攻击目的

## Django怎么验证一个请求是不是 CSRF ？
- Django 处理客户端请求时，会生成一个随机 Token ，放到 Cookie 里一起返回，然后需要前端每次 POST 请求时带上这个 Token ，可以放到 POST 数据里键为 csrfmiddlewaretoken ，或者放到请求头键为 X-CSRFToken ， Django 从这两个位置取，每次处理都会拦截验证，通过比对两者是否一致来判断这个请求是不是非法，非法就返回403状态码

## 常见有三种方法可以携带 CSRF Token 发送给服务端
- from 表单添加 {% csrf_token %} 标签，表单会携带一同提交
    ```html
    <!--login.html-->
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Title</title>
    </head>
    <body>
    <form action="/login/", method="post">
        <!--添加 csrf token-->
        {% csrf_token %}
        用户名：<input type="text" name="username">
        密码：<input type="text" name="password">
        <input type="submit" value="登录">
    </form>
    <p>{{ msg }}</p>
    </body>
    </html>
    ```
- 如果是 Ajax 请求，需要把 csrf token 字符串（也是通过拿 {% csrf_token %} 标签产生的值）放到 data 里一起提交，并且键名为 csrfmiddlewaretoken 或者放到请求头传递服务端
    ```js
    var csrf_token = $("[name='csrfmiddlewaretoken']").val();
    var data = {'id': '123', 'csrfmiddlewaretoken': csrf_token};
    $.ajax({
        type: "POST",
        url: "/api",
        data: data,
        dataType: 'json'
    })
    ```
- 指定取消某函数视图 CSRF 防护
    ```python
    # views.py
    from django.views.decorators.csrf import csrf_exempt

    @csrf_exempt
    def index(request):
        return render(request,'index.html')
    ```