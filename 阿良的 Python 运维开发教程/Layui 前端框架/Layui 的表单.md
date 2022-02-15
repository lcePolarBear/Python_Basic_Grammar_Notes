# Layui 的表单

## 创建 layui 表单模板
1. [官方表单文档](https://www.layui.com/doc/element/form.html)
2. 导入并修改表单模板代码
    ```html
    <!--调用模板-->
    {% extends 'base.html' %}
    {% block title %}首页{% endblock %}
    {% block content %}

    <!--为 layui 调用 js 文件-->
    <script src="/static/layui/layui.js"></script>

    <form class="layui-form">
        {% csrf_token %}
    <div class="layui-form-item">
        <label class="layui-form-label">用户名</label>
        <div class="layui-input-block">
        <input type="text" name="username" required  lay-verify="required" placeholder="请输入用户名" autocomplete="off" class="layui-input">
        </div>
    </div>
    <div class="layui-form-item">
        <label class="layui-form-label">密码</label>
        <div class="layui-input-inline">
        <input type="password" name="password" required lay-verify="required" placeholder="请输入密码" autocomplete="off" class="layui-input">
        </div>
        <div class="layui-form-mid layui-word-aux">注意：密码必须大于 8 位，小于 16 位</div>
    </div>
    <div class="layui-form-item">
        <label class="layui-form-label">城市</label>
        <div class="layui-input-block">
        <select name="city" lay-verify="required">
            <option value=""></option>
            <option value="0">北京</option>
            <option value="1">上海</option>
            <option value="2">广州</option>
            <option value="3">深圳</option>
            <option value="4">杭州</option>
        </select>
        </div>
    </div>
    <div class="layui-form-item">
        <label class="layui-form-label">爱好</label>
        <div class="layui-input-block">
        <input type="checkbox" name="like[write]" title="写作">
        <input type="checkbox" name="like[read]" title="阅读" checked>
        <input type="checkbox" name="like[dai]" title="发呆">
        </div>
    </div>
    <div class="layui-form-item">
        <label class="layui-form-label">是否启用</label>
        <div class="layui-input-block">
        <input type="checkbox" name="switch" lay-skin="switch">
        </div>
    </div>
    <div class="layui-form-item">
        <label class="layui-form-label">性别</label>
        <div class="layui-input-block">
        <input type="radio" name="sex" value="男" title="男">
        <input type="radio" name="sex" value="女" title="女" checked>
        </div>
    </div>
    <div class="layui-form-item layui-form-text">
        <label class="layui-form-label">信息备注</label>
        <div class="layui-input-block">
        <textarea name="desc" placeholder="请输入内容" class="layui-textarea"></textarea>
        </div>
    </div>
    <div class="layui-form-item">
        <div class="layui-input-block">、
            <!--lay-filter="formdemo" 相当于选择一个事件标识，用于执行 js 事件-->
        <button class="layui-btn" lay-submit lay-filter="formDemo">立即提交</button>
        <button type="reset" class="layui-btn layui-btn-primary">重置</button>
        </div>
    </div>
    </form>

    <script>
    //Demo
    layui.use('form', function(){
        var form = layui.form;
        var layer = layui.layer
        var $ = layui.jquery

        //监听提交
        form.on('submit(formDemo)', function(data){
            console.log(data)
            $.ajax({
                type: "POST",
                url: "/form_api",
                data: data.field,
                success: function (result) {
                    if (result.code == "0"){
                        layer.msg(result.msg)
                    }else {
                        layer.msg("为啥错了？")
                    }
                },
                error: function () {
                    layer.msg("服务器接口异常")
                }
            })
        });
    });
    </script>

    {% endblock %}
    ```
3. 创建后端响应
    ```py
    # views.py
    def form_api(request):
        if request.method == "POST":
            print(request.POST)
            code = "0"
            msg = "添加用户成功"
            result = {'code': code, 'msg': msg}
            return JsonResponse(result)
    ```