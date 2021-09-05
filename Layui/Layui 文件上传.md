# Layui 文件上传
## 创建 Layui 文件上传模板
1. 官方文件上传文档
2. 导入并修改示例代码
    ```html
    {% extends 'base.html' %}
    {% block title %}首页{% endblock %}
    {% block content %}

    {% csrf_token %}
    <button type="button" class="layui-btn" id="test1">
    <i class="layui-icon">&#xe67c;</i>上传图片
    </button>

    <script src="/static/layui/layui.js"></script>
    <script>
    layui.use('upload', function(){
        var upload = layui.upload;
        var $ = layui.jquery

            //手动添加 token
        var csrf_token = $('[name="csrfmiddlewaretoken"]').val();

        //执行实例
        var uploadInst = upload.render({
            elem: '#test1' //绑定元素
            ,url: 'upload' //上传接口
            ,data: {'csrfmiddlewaretoken':csrf_token}   //添加 csrf 信息，data 用于请求上传接口的额外参数
            ,done: function(res){
            //上传完毕回调
            }
            ,error: function(){
            //请求异常回调
            }
        });
    });
    </script>

    {% endblock %}
    ```
3. 创建处理上传数据的后端
    ```python
    def file(request):
        if request.method == "POST":
            import os
            # 将文件信息写入目录
            file_obj = request.FILES.get('file')
            file_path = os.path.join('upload', file_obj.name)
            with open(file_path, mode='wb') as f:
                for i in file_obj.chunks():
                    f.write(i)
            code = "0"
            msg = "文件上传成功"
            result = {'code': code, 'msg': msg}
            return JsonResponse(result)
    ```