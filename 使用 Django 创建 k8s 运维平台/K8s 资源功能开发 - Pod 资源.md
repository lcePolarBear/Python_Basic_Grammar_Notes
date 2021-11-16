# K8s 资源功能开发 - Pod 资源
- 实现思路与 deployment 资源一致，都是通过前端动态数据表格展示 + 后端 api 返回数据实现资源展示，只是通过浏览器缓存读取 namespace 数据用于返回指定命名空间下的 statefulset 资源
```python
# workload/views.py
@k8s.self_login_required
def pod(request):
    return render(request, "workload/pods.html")


@k8s.self_login_required
def pod_api(request):
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    list = []
    k8s.laod_auth_config(auth_type=auth_type, token=token)
    core_api = client.CoreV1Api()

    if request.method == "GET":
        try:
            search_key = request.GET.get('search_key')
            current_namespace = request.GET.get("namespace")
            for pod in core_api.list_namespaced_pod(current_namespace).items:
                name = pod.metadata.name
                namespace = pod.metadata.namespace
                labels = pod.metadata.labels
                pod_ip = pod.status.pod_ip
                containers = []
                status = "None"
                if pod.status.container_statuses is None:
                    status = pod.status.conditions[-1].reason
                else:
                    for c in pod.status.container_statuses:
                        c_name = c.name
                        c_image = c.image
                        # 获取重启次数
                        restart_count = c.restart_count
                        # 获取容器状态
                        c_status = "None"
                        if c.ready is True:
                            c_status = "Running"
                        elif c.ready is False:
                            if c.state.waiting is not None:
                                c_status = c.state.waiting.reason
                            elif c.state.terminated is not None:
                                c_status = c.state.terminated.reason
                            elif c.state.last_state.terminated is not None:
                                c_status = c.last_state.terminated.reason
                        c = {'c_name': c_name, 'c_image': c_image, 'restart_count': restart_count, 'c_status': c_status}
                        containers.append(c)
                create_time = pod.metadata.creation_timestamp

                item = {"name": name, "namespace": namespace, "pod_ip": pod_ip,
                        "labels": labels, "containers": containers, "status": status,
                        "create_time": create_time}
                if search_key:
                    if search_key == name:
                        list.append(item)
                else:
                    list.append(item)
            code = 0
            msg = "success!"
        except Exception as e:
            msg = str(e)
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
            core_api.delete_namespaced_pod(name=name, namespace=current_namespace)
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
{% block title %}Pods{% endblock %}
{% block nav-item-2 %}layui-nav-itemed{% endblock %}
{% block nav-child-2-1 %}layui-this{% endblock %}
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
                    <a class="layui-btn layui-btn-danger layui-btn-xs" lay-event="del">重建</a>
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
                , url: '{% url 'pod_api' %}?namespace=' + namespace //数据接口
                , page: true //开启分页
                , cols: [[ //表头
                    {field: 'name', title: '名称', sort: true}
                    , {field: 'namespace', title: '命名空间', sort: true}
                    , {field: 'pod_ip', title: 'IP地址'}
                    , {field: 'labels', title: '标签', templet: labelsFormat}
                    , {field: 'containers', title: '容器组', templet: containersFormat}
                    , {field: 'status', title: '状态', sort: true, templet: statusFormat}
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
                        result += '<span style="border: 1px solid #009688;border-radius: 5px">' + key + ':' + d.labels[key] + '</span><br>'
                    }
                    return result
                }
            }

            function containersFormat(d) {
                result = "";
                if (d.containers) {
                    for (let key in d.containers) {
                        data = d.containers[key];
                        result += key + ':' + data.c_name + '=' + data.c_image + '<br>' +
                            '重启次数:' + data.restart_count + '<br>' +
                            '状态:' + data.c_status + '<br>'
                    }
                    return result
                } else {
                    return "None"
                }
            };

            function statusFormat(d) {
                result = "";
                if (d.status == "None") {
                    for (let key in d.containers) {
                        result += d.containers[key].c_status + '<br>'
                    }
                    return result
                } else {
                    return d.status
                }
            }

            //监听行工具事件
            table.on('tool(test)', function (obj) {
                var data = obj.data;
                //console.log(obj)
                if (obj.event === 'del') {
                    layer.confirm('Are you sure to want reload the pod : ' + data.name + ' ?', function (index) {
                        var csrf_token = $('[name="csrfmiddlewaretoken"]').val();
                        $.ajax({
                            type: "DELETE",
                            url: "{% url 'pod_api' %}",
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
### 实现容器日志功能
```js
// template/workload/pod.html
{% block ex_form %}
    <div id="log" style="display: none">
        <div id="log-text" style="background-color: black;color: white;padding: 10px;font-size: 16px"></div>
    </div>
{% endblock %}

table.on('tool(test)', function (obj) {
    var data = obj.data;
    //console.log(obj)
    if (obj.event === 'del') {
        layer.confirm('Are you sure to want reload the pod : ' + data.name + ' ?', function (index) {
            $.ajax({
                type: "DELETE",
                url: "{% url 'pod_api' %}",
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
    } else if (obj.event === 'yaml') {
        layer.open({
            title: "YAML",
            type: 2,
            area: ["60%", "70%"],
            closeBtn: 1, //关闭按钮
            content: '{%  url 'ace_editor' %}?resource=pod&' + 'namespace=' + data.namespace + '&name=' + data.name
        })
    } else if (obj.event === 'log') {
        $.ajax({
            type: "GET"
            , async: false
            , url: "{% url 'pod_log' %}?namespace=" + data.namespace + '&name=' + data.name
            , success: function (res) {
                if (res.code == 0) {
                    $('#log-text').html("<pre>" + res.data + "</pre>")
                } else {
                    $('#log-text').html("<pre>" + res.msg + "</pre>")
                }
            }, error: function () {
                layer.open({
                    type: 0,
                    title: ['异常信息'],
                    content: "服务器接口异常！"
                })
            }
        });
        layer.open({
            title: "Pod 日志"
            , type: 1
            , area: ["60%", "70%"]
            , content: $("#log").html()
        })
    }
});
```
```python
# workload/views.py
@k8s.self_login_required
def pod_log(request):
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    k8s.laod_auth_config(auth_type, token)
    core_api = client.CoreV1Api()

    name = request.GET.get("name", None)
    namespace = request.GET.get("namespace", None)

    # 目前没有对Pod多容器处理
    try:
        log_text = core_api.read_namespaced_pod_log(name=name, namespace=namespace, tail_lines=500)
        if log_text:
            code = 0
            msg = "获取日志成功！"
        elif len(log_text) == 0:
            code = 0
            msg = "没有日志！"
            log_text = "没有日志！"
            print(11111)
    except Exception as e:
        msg = str(e)
        code = 1
        log_text = "获取日志失败！"
    res = {"code": code, "msg": msg, "data": log_text}
    return JsonResponse(res)
```
### 实现容器终端功能
- 加载前端库 xterm.js
- 使用 Channels 在 Django 创建 websocket 通信