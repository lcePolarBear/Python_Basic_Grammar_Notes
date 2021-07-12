# HttpResponse 对象

## render 函数
- render 指定模板，返回一个渲染后的 HttpResponse 对象
- 语法 `render(request, template_name, context=None, content_type=None, status=None, using=None)`
    - request: 固定参数， django 的封装请求
    - template_name: 返回的 html 模板
    - context： 传入模板中的内容，用于渲染模板，默认空字典
- 示例
    ```python
    # views.py
    from django.shortcuts import render

    def index(request):
        return render(request, "index.html", {'result':"欢迎你访问！"})
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
    <h1>首页</h1>
    <span>{{ result }}</span>
    </body>
    </html>
    ```

## redirect 函数
- 重定向，发起第二次请求
- 语法 `redirect(to, *args, **kwargs)`
- 参数可以是：一个视图，一个绝对或者相对的 URL，一个模型、对象是重定向的 URL
- 示例
    ```python
    # views.py
    from django.shortcuts import redirect

    def index(request):
        return redirect("http://www.baidu.com")
    ```

## StreamingHttpResponse 函数
- 流式响应可迭代对象
- 示例：下载文件
    ```python
    # urls.py
    from django.urls import path,re_path

    urlpatterns = [
        re_path('^download/$', views.download, name="download"),
        re_path('^down_file/(?P<file_name>.*)', views.down_file, name="down_file")
    ]
    ```
    ```python
    # views.py
    from django.http import StreamingHttpResponse
    from django.shortcuts import render
    import os

    def download(request):
        file_list = os.listdir("upload")
        return render(request, "index.html", {'files':file_list})

    def down_file(request, file_name):
        print(request.path)
        file_path = os.path.join('upload', file_name)
        response = StreamingHttpResponse(open(file_path, 'rb'))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment; filename=%s' %(os.path.basename(file_path))
        return response
    ```
    ```html
    <!--download.html-->
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Title</title>
    </head>
    <body>
    <h1>首页</h1>
    {% for foo in files %}
        <a href="{% url 'down_file' foo %}">{{ foo }}</a><br>
    {% endfor %}
    </body>
    </html>
    ```

## FileResponse 函数
- 建议替代 StreamingHttpResponse 用于文件下载
- 示例：代码同上，将 StreamingHttpResponse 替换为 FileResponse 即可
    ```python
    def down_file(request, file_name):
        print(request.path)
        file_path = os.path.join('upload', file_name)
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment; filename=%s' %(os.path.basename(file_path))
        return response
    ```

## JsonResponse 函数
- 响应一个 Json 对象
- 示例：返回 json 数据
    ```python
    # views.py
    from django.http import JsonResponse

    def json_api(request):
        res = {'a':123,'b':456}
        return JsonResponse(res)
    ```
