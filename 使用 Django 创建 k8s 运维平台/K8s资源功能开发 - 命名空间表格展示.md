# K8s资源功能开发 - 命名空间表格展示

### 创建一个数据表格
```js
// namespace.html
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
```js
// namespace.html
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