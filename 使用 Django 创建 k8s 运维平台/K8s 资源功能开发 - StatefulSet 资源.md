# K8s 资源功能开发 - StatefulSet 资源
- 实现思路与 deployment 资源一致，都是通过前端动态数据表格展示 + 后端 api 返回数据实现资源展示，只是通过浏览器缓存读取 namespace 数据用于返回指定命名空间下的 statefulset 资源
```python
# workload/views.py
@k8s.self_login_required
def statefulset(request):
    return render(request, "workload/statefulsets.html")


@k8s.self_login_required
def statefulset_api(request):
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    list = []
    k8s.laod_auth_config(auth_type=auth_type, token=token)
    app_api = client.AppsV1Api()

    if request.method == "GET":
        try:
            search_key = request.GET.get('search_key')
            current_namespace = request.GET.get("namespace")
            for sts in app_api.list_namespaced_stateful_set(current_namespace).items:
                name = sts.metadata.name
                namespace = sts.metadata.namespace
                replicas = sts.spec.replicas
                ready_replicas = (sts.status.ready_replicas if sts.status.ready_replicas else "0")
                labels = sts.metadata.labels
                selector = sts.spec.selector.match_labels
                service_name = sts.spec.service_name
                containers = {}
                for c in sts.spec.template.spec.containers:
                    containers[c.name] = c.image
                create_time = sts.metadata.creation_timestamp
                item = {"name": name, "namespace": namespace, "replicas": replicas,
                        "ready_replicas": ready_replicas, "labels": labels, "selector": selector,
                        "service_name": service_name,
                        "containers": containers, "create_time": create_time}
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
            app_api.delete_namespaced_stateful_set(name=name, namespace=current_namespace)
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
<!--template/workload/statefulset.html-->
{% extends 'base.html' %}
{% block title %}StatefulSets{% endblock %}
{% block nav-item-2 %}layui-nav-itemed{% endblock %}
{% block nav-child-2-4 %}layui-this{% endblock %}
{% block content %}
    {% csrf_token %}
    <div class="layui-card">
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
                , response: {
                    dataName: 'list'
                }
                , url: '{% url 'statefulset_api' %}?namespace=' + namespace //数据接口
                , page: true //开启分页
                , cols: [[ //表头
                    {field: 'name', title: '名称', sort: true}
                    , {field: 'namespace', title: '命名空间', sort: true}
                    , {field: 'service_name', title: 'Service名称'}
                    , {field: 'replicas', title: '预期副本数', width: 100}
                    , {field: 'ready_replicas', title: '可用副本数', width: 100}
                    , {field: 'labels', title: '标签', templet: labelsFormat}
                    , {field: 'selector', title: 'Pod 标签选择器', templet: selecotrFormat}
                    , {field: 'containers', title: '容器', templet: containersFormat}
                    , {field: 'create_time', title: '创建时间', width: 200}
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
                        result += '<span style="border: 1px solid #009688;border-radius: 5px">' + key + ':' + d.labels[key] + '</span><br>'
                    }
                    return result
                }
            }

            function selecotrFormat(d) {
                result = "";
                for (let key in d.selector) {
                    result += '<span style="border: 1px solid #009688;border-radius: 5px">' + key + ':' + d.selector[key] + '</span><br>'
                }
                return result
            }

            function containersFormat(d) {
                result = "";
                for (let key in d.containers) {
                    result += '<span style="border: 1px solid #009688;border-radius: 5px">' + key + ':' + d.containers[key] + '</span><br>'
                }
                return result
            }

            //监听行工具事件
            table.on('tool(test)', function (obj) {
                var data = obj.data;
                //console.log(obj)
                if (obj.event === 'del') {
                    layer.confirm('Are you sure to wang delete the statefulset : ' + data.name + ' ?', function (index) {
                        var csrf_token = $('[name="csrfmiddlewaretoken"]').val();
                        var info = {"name": data.name, "namespace": namespace}
                        $.ajax({
                            type: "DELETE",
                            url: "{% url 'statefulset_api' %}",
                            data: data,
                            headers: {'X-CSRFToken': csrf_token},
                            success: function (res) {
                                if (res.code == 0) {
                                    obj.del();  // 删除当前页面数据
                                    layer.msg(res.msg, {icon: 6, time: 6000}) // 默认停顿3秒
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