# K8s 资源功能开发 - Namespace 资源

### 创建一个数据表格
```html
<!-- template/k8s/namespace.html -->
# templates/k8s/namespace.html
{% extends 'base.html' %}
{% block title %}Namespaces{% endblock %}
{% block nav-item-1 %}layui-nav-itemed{% endblock %}
{% block nav-child-1-2 %}layui-this{% endblock %}
{% block content %}
    {% csrf_token %}
    <div class="layui-card">
        <div class="layui-card-body">
            <table id="demo" lay-filter="test"></table>
        </div>
    </div>
{% endblock %}
{% block ex_js %}
<script>
layui.use('table', function(){
    var table = layui.table;
    var $ = layui.jquery;
    //第一个实例
    table.render({
        elem: '#demo'
        ,response: {
            dataName: 'list'    ////规定数据列表的字段名称，默认：data
        }
        ,height: 312
        ,url: '{% url 'namespace_api' %}' //数据接口
        ,page: true //开启分页
        ,cols: [[ //表头
          {field: 'name', title: '名称', width:240, sort: true, fixed: 'left'}
          ,{field: 'labels', title: '标签', width:240 }
          ,{field: 'create_time', title: '创建时间', width:240}
        ]]
    });
});
</script>
{% endblock %}
```

### 实现 namespace 资源多标签显示
```html
<!-- template/k8s/namespace.html -->
{% block ex_js %}
<script>
layui.use('table', function(){
    var table = layui.table;
    var $ = layui.jquery;
    //第一个实例
    table.render({
        elem: '#demo'
        ,response: {
            dataName: 'list'
        }
        ,url: '{% url 'namespace_api' %}' //数据接口
        ,page: true //开启分页
        ,cols: [[ //表头
          {field: 'name', title: '名称', width:240, sort: true}
          ,{field: 'labels', title: '标签', width:240, templet : labels_table}
          ,{field: 'create_time', title: '创建时间', width:240}
        ]]
    });
    // 实现标签内容的的调出
    function labels_table(d){
        if (d.labels == null) {
            return "None"
        }else{
            var result = ""
            for (let key in d.labels){
                result += '<span>' + key + ':' + d.labels[key] + '</span><br>'
            }
            return result
        }
    }
});
</script>
{% endblock %}
```
- 一个单元格需要展示多个标签则需要在样式添加表格换行样式
```html
// base.html
<link rel="stylesheet" href="/static/layui/css/layui.css">
    <style>
        .namespace {
            margin-top: 10px;
        }
        .namespace select, .namespace option {
            width: 200px;
            height: 40px;
            font-size: 16px;
        }
        /*实现 table 表格的d单元格多行内容换行*/
        .layui-table-cell{
            height: 100%;
        }
    </style>
```

### 实现 namespace 资源搜索
- 添加搜索框
```html
// namespace.html
{% block content %}
    {% csrf_token %}
    <div class="layui-card">
        <div class="layui-card-body layui-row">
            <div class="layui-col-md12 layui-col-space10">
                <button class="layui-btn" style="float: left" id="create">创建资源</button>
                <button class="layui-btn" style="float: right" id="searchBtn">搜索资源</button>
                <input type="text" name="name" class="layui-input" style="float: right; width: 300px">
            </div>
            <div class="layui-col-md12">
                <table id="demo" lay-filter="test"></table>
                <!--添加工具条-->
                <script type="text/html" id="barDemo">
                <a class="layui-btn layui-btn-primary layui-btn-xs" lay-event="yaml">查看 YAML</a>
                <a class="layui-btn layui-btn-danger layui-btn-xs" lay-event="del">删除</a>
                </script>
            </div>
        </div>
    </div>
{% endblock %}
```
- 通过动态表格数据重载实现搜索后数据刷新
```js
// 实现资源搜索功能
$('#searchBtn').click(function () {
    var search_key = $('input[name="name"]').val()
    table.reload('TT', {
        where: {
            search_key: search_key
        }
    })
})
```
- 后台提供数据表格重载的信息接口
```python
# k8s/views.py/namespace_api
try:
    search_key = request.GET.get('search_key')
    for ns in core_api.list_namespace().items:
        name = ns.metadata.name
        labels = ns.metadata.labels
        create_time = ns.metadata.creation_timestamp
        item = {'name': name, 'labels': labels, 'create_time': create_time}
        # 判断是否为查询情况
        if search_key:
            if search_key == name:
                list.append(item)
        else:
            list.append(item)
    code = 0
    msg = "success!"
except Exception as e:
    status = getattr(e, 'status')
    code = str(status)
    msg = "faild!"
```
### 实现 namespace 资源的添加
- 使用 layer 配合 form 实现信息的提交
```html
<!--首先创建一个 form 表单，然后通过提交到后台实现资源的创建-->
<!--base.html-->
<!--layer 的 form 最好放在 body 标签以外，所以在 base.html 额外使用一个 block 接入 form-->
<!--.......-->
</body>
{% block ex_form %}{% endblock %}
</html>

<!--namespace.html-->
{% block ex_form %}
    <div id="ck">
        <form class="layui-form" onsubmit="return false">
            <div class="layui-form-item">
                <label class="layui-form-label" style="width: 160px">namespace 资源名称：</label>
                <div class="layui-input-block">
                    <input type="text" name="title" required lay-verify="required" placeholder="请输入" autocomplete="off"
                           class="layui-input" style="width: 200px">
                </div>
            </div>
            <div class="layui-form-item">
                <div class="layui-input-block">
                    <button class="layui-btn" lay-submit lay-filter="formDemo">提交</button>
                </div>
            </div>
        </form>
    </div>
{% endblock %}

{% block ex_js %}
    <script>
        layui.use(['table', 'form'], function () {
            var $ = layui.jquery;
            var csrf_token = $('[name="csrfmiddlewaretoken"]').val();   //获取 csrf
            var table = layui.table;
            var form = layui.form;
            var layer = layui.layer

            ....

            // 创建按钮触发创建 namespace 资源事件
            $('#create').on('click', function () {
                layer.open({
                    title: "create namespace resource"
                    , type: 1   // 1 表示以页面为内容载体弹出
                    , content: $("#ck").html()
                    , area: ['400px', '200px']
                    , success: function () {
                        form.on('submit(formDemo)', function (data) {
                            $.ajax({
                                url: '{% url "namespace_api" %}'
                                , type: 'POST'
                                , data: data.field
                                , headers: {'X-CSRFToken': csrf_token}
                                , dataType: 'json'
                                // 提交成功回调函数
                                , success: function (res) {
                                    if (res.code == '0') {
                                        layer.msg(res.msg, {icon: 6, time: 4000});
                                        window.location.reload()
                                    } else {
                                        layer.msg(res.msg, {icon: 5})
                                    }
                                }
                                // 访问接口失败函数
                                , error: function (res) {
                                    layer.msg("服务器接口异常！", {icon: 5})
                                }
                            })
                        })
                    }
                })
            })
```
```python
# k8s/views.py
def namespace_api(request):
    """
    内容忽略
    """
    elif request.method == "POST":
        name = request.POST.get("title")
        body = client.V1Namespace(
            api_version="v1"
            , kind="Namespace"
            , metadata=client.V1ObjectMeta(
                name=name
            )
        )
        try:
            core_api.create_namespace(body=body)
            code = 0
            msg = "success!"
        except Exception as e:
            msg = str(e)
            code = 1
        result = {'code': code, 'msg': msg}
    return JsonResponse(result) 
```