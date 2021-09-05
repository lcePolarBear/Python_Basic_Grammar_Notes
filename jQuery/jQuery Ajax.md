# jQuery Ajax
- Ajax 是一种在无需重新加载整个网页的情况下，能够更新部分网页的技术
- 例如在不刷新页面的情况下查询数据、登录验证等

### jQuery Ajax 主要使用 $.ajax() 方法实现，用于向服务端发送 HTTP 请求
- 语法： `$.ajax([settings]);`
- settings 是 $.ajax() 方法的参数列表，用于配置 Ajax 请求的键值对集合

    参数 | 类型 | 描述
    --- | --- | ---
    url | string | 发送请求的地址，默认为当前页地址
    type | string | 请求方式，默认为 GET
    data | object,array,string | 发送到服务器的数据
    dataType | string | 预期服务器返回的数据类型，包括JSON、XML、text、HTML等
    contentType | string | 发送信息至服务器时内容编码类型。默认值: "application/x-www-form-urlencoded"
    timeout | number | 设置请求超时时间
    global | Boolean | 表示是否触发全局 Ajax 事件，默认为 true
    headers | object | 设置请求头信息
    async | Boolean | 默认 true ，所有请求均为异步请求。设置 false 发送同步请求

### HTTP 方法
- 用于向服务器提交数据，服务器根据对应方法操作
- 常见的 http 方法：
    http 方法 | 数据处理 | 说明
    --- | --- | ---
    post | 新增 | 新增一个资源
    get | 获取 | 获得一个资源
    put | 更新 | 更新一个资源
    delete | 删除 | 删除一个资源

### 回调函数
- 回调函数：参数引用一个函数，并将数据作为参数传递给该函数

    参数 | 函数格式 | 描述
    --- | --- | ---
    beforeSend | function(jqXHR, object) | 发送请求前调用的函数，例如添加自定义 HTTP 头
    success | function(data, String, textStatus, jqXHR) | 请求成功后调用的函数，参数data：可选，由服务器返回的数据
    error | function(jqXHR, String, textStatus, errorThrown) | 请求失败时调用的函数
    complete | function(jqXHR, String, textStatus) | 请求完成后（无论成功还是失败）调用的函数
    > jqXHR：一个 XMLHttpRequest 对象

### 使用 Ajax 从后台获取数据
```js
<!--index.html-->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <script type="text/javascript" src="https://cdn.bootcdn.net/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
</head>
<body>
<div id="demo">

</div>
<script type="text/javascript">
    $.ajax({
        type:"GET",
        url:"/jquery_api",
        success: function (result) {
            if (result.code == '0'){
                for (var i in result.user)
                $("#demo").append("<p>" + i + ":" + result.user[i] + "</p>")
            }else if (result.code == '1'){
                alert("发起请求成功，但是状态码为 1")
            }
        },
        error: function () {
            alert("无法发起请求")
        }
    })
</script>
</body>
</html>
```
```python
# views.py
from django.http import JsonResponse
from django.shortcuts import render

def ajax_api(request):
    if request.method == "GET":
        user = {'user1': 'aliang', 'user2': 'aliang'}
        code = 0
        msg = "请求成功"
        data = {'user': user,'code': code,'msg': msg}
        return JsonResponse(data)
    else:
        msg = "无权限操作"
        return msg

def index(request):
    return render(request,"index.html")
```
