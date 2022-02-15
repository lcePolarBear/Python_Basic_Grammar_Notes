# K8s 资源功能开发 - ConfigMap 资源
```python
def configmap(request):
    return render(request, "storage/configmaps.html")


def configmap_api(request):
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    list = []
    k8s.laod_auth_config(auth_type=auth_type, token=token)
    core_api = client.CoreV1Api()

    if request.method == "GET":
        try:
            search_key = request.GET.get('search_key')
            current_namespace = request.GET.get("namespace")
            for cm in core_api.list_namespaced_config_map(current_namespace).items:
                name = cm.metadata.name
                namespace = cm.metadata.namespace
                data_length = ("0" if cm.data is None else len(cm.data))
                create_time = cm.metadata.creation_timestamp

                item = {"name": name, "namespace": namespace, "data_length": data_length, "create_time": create_time}
                if search_key:
                    if search_key == name:
                        list.append(item)
                else:
                    list.append(item)
            code = 0
            msg = "success!"
        except Exception as e:
            msg = str(getattr(e, 'status'))
            code = 1
        if request.GET.get('page'):
            current_page = int(request.GET.get('page', 1))
            page_item_num = int(request.GET.get('limit'))
            start = (current_page - 1) * page_item_num
            end = current_page * page_item_num
            list = list[start:end]
        result = {'code': code, 'msg': msg, 'count': len(list), 'list': list}
    if request.method == "DELETE":
        request_date = QueryDict(request.body)
        name = request_date.get("name")
        current_namespace = request_date.get("namespace")
        try:
            core_api.delete_namespaced_config_map(name=name, namespace=current_namespace)
            code = 0
            msg = "delete operation success!"
        except Exception as e:
            code = 1
            msg = str(e)
        result = {'code': code, 'msg': msg}
        return JsonResponse(result)
    return JsonResponse(result)
```
```html
{% extends 'base.html' %}
{% block title %}ConfigMaps{% endblock %}
{% block nav-item-4 %}layui-nav-itemed{% endblock %}
{% block nav-child-4-1 %}layui-this{% endblock %}
{% block content %}
    {% csrf_token %}
    <div class="layui-card-body layui-row">
        <div class="layui-col-space10  layui-col-md12">
            <div class="layui-col-md12">
                <button class="layui-btn" style="float: left">创建</button>
                <button class="layui-btn" style="float: right" id="searchBtn">搜索</button>
                <input type="text" name="name" class="layui-input" style="width: 150px;float: right;margin-left: 20px">
            </div>
            <div class="layui-col-md12">
                <table id="test" lay-filter="test"></table>
                <script type="text/html" id="barDemo">
                    <a class="layui-btn layui-btn-xs layui-btn-primary" lay-event="yaml">YAML</a>
                    <a class="layui-btn layui-btn-danger layui-btn-xs" lay-event="del">删除</a>
                </script>
            </div>
        </div>
    </div>
{% endblock %}
{% block ex_js %}
    <script>

        // 获取当前命名空间
        var storage = window.sessionStorage;
        var namespace = storage.getItem('namespace');

        layui.use('table', function () {
            var table = layui.table;
            var $ = layui.jquery;
            //动态渲染表格
            table.render({
                elem: '#test'
                , url: '{% url 'configmap_api' %}?namespace=' + namespace //数据接口
                , response: {
                    dataName: 'list'
                }
                , page: true //开启分页
                , cols: [[ //表头
                    {field: 'name', title: '名称', sort: true}
                    , {field: 'namespace', title: '命名空间', sort: true}
                    , {field: 'data_length', title: '数据数量'}
                    , {field: 'create_time', title: '创建时间'}
                    , {fixed: 'right', title: '操作', toolbar: '#barDemo', width: 150}
                ]]
                , id: "TT"
            });

            // 标签格式化
            function labelsFormat(d) {
                result = "";
                if (d.labels == null) {
                    return "None"
                } else {
                    for (let key in d.labels) {
                        result += '<span style="border: 1px solid #d6e5ec;border-radius: 8px">' +
                            key + ':' + d.labels[key] +
                            '</span><br>'
                    }
                    return result
                }
            }

            //监听行工具事件
            table.on('tool(test)', function (obj) {
                var data = obj.data;
                //console.log(obj)
                if (obj.event === 'del') {
                    layer.confirm('你要真要删除' + data.name + ' ConfigMap吗？', function (index) {
                        var csrf_token = $('[name="csrfmiddlewaretoken"]').val();
                        var info = {"name": data.name, "namespace": data.namespace}
                        $.ajax({
                            type: "DELETE",
                            url: "{% url 'configmap_api' %}",
                            data: info,
                            headers: {'X-CSRFToken': csrf_token},
                            success: function (res) {
                                if (res.code == 0) {
                                    obj.del();  // 删除当前页面数据
                                    layer.msg(res.msg, {icon: 6, time: 3000}) // 默认停顿3秒
                                } else {
                                    layer.msg(res.msg, {icon: 5})
                                }
                            },
                            error: function () {
                                layer.open({
                                    type: 0,
                                    title: ['异常信息'],
                                    content: "服务器接口异常！"
                                })
                            }
                        });
                        layer.close(index);
                    });
                } else if (obj.event === 'edit') {
                    // 查看YAML
                }
            });
            // 监控搜索事件
            $('#searchBtn').click(function () {
                var search_key = $('input[name="name"]').val()
                table.reload('TT', {
                    where: {
                        search_key: search_key
                    }
                });
            })

        });
    </script>
{% endblock %}
```