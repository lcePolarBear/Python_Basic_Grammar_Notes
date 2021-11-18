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
- 使用 Channels 在 Django 创建 websocket 通信（注意版本需为 2.4.0）
```js
// template/workload/terminal.html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>容器终端</title>
    <link href="/static/xterm/xterm.css" rel="stylesheet" type="text/css"/>
    <style>
        body {
            background-color: black
        }

        .terminal-window {
            background-color: #2f4050;
            width: 99%;
            color: white;
            line-height: 25px;
            margin-bottom: 10px;
            font-size: 18px;
            padding: 10px 0 10px 10px
        }

        .containers select, .containers option {
            width: 100px;
            height: 25px;
            font-size: 18px;
            color: #2F4056;
            text-overflow: ellipsis;
            outline: none;
        }
    </style>
</head>

<body>
<div class="terminal-window">
    <div class="containers">
        Pod名称：{{ connect.pod_name }}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        容器：
        <select name="container_name" id="containerSelect">
            {% for c in connect.containers %}
                <option value="{{ c }}">{{ c }}</option>
            {% endfor %}
        </select>
    </div>
</div>
<div id="terminal" style="width: 100px;"></div>
</body>

<script src="/static/xterm/xterm.js"></script>

<script>

    var term = new Terminal({cursorBlink: true, rows: 70});
    term.open(document.getElementById('terminal'));

    var auth_type = '{{ connect.auth_type }}';
    var token = '{{ connect.token }}';
    var namespace = '{{ connect.namespace }}';
    var pod_name = '{{ connect.pod_name }}';
    var container = document.getElementById('containerSelect').value;

    // 打开一个 websocket，django也会把sessionid传过去
    var ws = new WebSocket('ws://' + window.location.host + '/workload/terminal/' + namespace + '/' + pod_name + '/' + container + '/?auth_type=' + auth_type + '&token=' + token);

    //打开websocket连接，并打开终端
    ws.onopen = function () {
        // 实时监控输入的字符串发送到后端
        term.on('data', function (data) {
            ws.send(data);
        });

        ws.onerror = function (event) {
            console.log('error:' + e);
        };
        //读取服务器发送的数据并写入web终端
        ws.onmessage = function (event) {
            term.write(event.data);
        };
        // 关闭websocket
        ws.onclose = function (event) {
            term.write('\n\r\x1B[1;3;31m连接关闭！\x1B[0m');
        };
    };

</script>
</html>

// template/workload/pods.html
table.on('tool(test)', function (obj) {
    var data = obj.data;
    //console.log(obj)
    if (obj.event === 'del') {
        //
    } else if (obj.event === 'yaml') {
        //
    } else if (obj.event === 'log') {
        //
    } else if (obj.event === 'terminal') {
        // 逗号拼接容器名, 例如containers=c1,c2
        cs = data['containers'];
        containers = "";
        for (let c in cs) {
            if (c < cs.length - 1) {
                containers += cs[c]['c_name'] + ","
            } else {
                containers += cs[c]['c_name']
            }
        }
        layer.open({
            title: "容器终端",
            type: 2,  // 加载层，从另一个网址引用
            area: ['50%', '60%'],
            content: '{% url "terminal" %}?namespace=' + data["namespace"] + "&pod_name=" + data["name"] + "&containers=" + containers,
        });
    }
});
```
```python
# workload/views.py
from django.views.decorators.clickjacking import xframe_options_exempt
@xframe_options_exempt
@k8s.self_login_required
def terminal(request):
    namespace = request.GET.get("namespace")
    pod_name = request.GET.get("pod_name")
    containers = request.GET.get("containers").split(',')  # 返回 nginx1,nginx2，转成一个列表方便前端处理
    auth_type = request.session.get(
        'auth_type')  # 认证类型和token，用于传递到websocket，websocket根据sessionid获取token，让websocket处理连接k8s认证用
    token = request.session.get('token')
    connect = {'namespace': namespace, 'pod_name': pod_name, 'containers': containers, 'auth_type': auth_type,
               'token': token}
    print("========")
    print(connect)
    return render(request, 'workload/terminal.html', {'connect': connect})
```
```python
# devops/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dashboard',
    'channels'
]

ASGI_APPLICATION = 'devops.routing.application'
```
```python
# devops/routing.py
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from django.urls import re_path
from devops.consumers import StreamConsumer

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([
            re_path(r'^workload/terminal/(?P<namespace>.*)/(?P<pod_name>.*)/(?P<container>.*)/', StreamConsumer),
        ])
    ),
})
```
```python
# devops/consumers.py
from channels.generic.websocket import WebsocketConsumer
from kubernetes.stream import stream
from threading import Thread
from kubernetes import client
from devops import k8s

# 多线程
class K8sStreamThread(Thread):
    def __init__(self, websocket, container_stream):
        Thread.__init__(self)
        self.websocket = websocket
        self.stream = container_stream

    def run(self):
        while self.stream.is_open():
            # 读取标准输出
            if self.stream.peek_stdout():
                stdout = self.stream.read_stdout()
                self.websocket.send(stdout)
            # 读取错误输出
            if self.stream.peek_stderr():
                stderr = self.stream.read_stderr()
                self.websocket.send(stderr)
        else:
            self.websocket.close()

# 继承WebsocketConsumer 类，并修改下面几个方法，主要连接到容器
class StreamConsumer(WebsocketConsumer):

    def connect(self):
        print("ok")
        # self.scope 请求头信息
        self.namespace = self.scope["url_route"]["kwargs"]["namespace"]
        self.pod_name = self.scope["url_route"]["kwargs"]["pod_name"]
        self.container = self.scope["url_route"]["kwargs"]["container"]

        k8s_auth = self.scope["query_string"].decode()  # b'auth_type=kubeconfig&token=7402e616e80cc5d9debe66f31b7a8ed6'
        auth_type = k8s_auth.split('&')[0].split('=')[1]
        token = k8s_auth.split('&')[1].split('=')[1]

        k8s.laod_auth_config(auth_type, token)
        core_api = client.CoreV1Api()

        exec_command = [
            "/bin/sh",
            "-c",
            'TERM=xterm-256color; export TERM; [ -x /bin/bash ] '
            '&& ([ -x /usr/bin/script ] '
            '&& /usr/bin/script -q -c "/bin/bash" /dev/null || exec /bin/bash) '
            '|| exec /bin/sh']
        try:

            self.conn_stream = stream(core_api.connect_get_namespaced_pod_exec,
                                 name=self.pod_name,
                                 namespace=self.namespace,
                                 command=exec_command,
                                 container=self.container,
                                 stderr=True, stdin=True,
                                 stdout=True, tty=True,
                                 _preload_content=False)
            kube_stream = K8sStreamThread(self, self.conn_stream)
            kube_stream.start()
        except Exception as e:
            print(e)
            status = getattr(e, "status")
            if status == 403:
                msg = "你没有进入容器终端权限！"
            else:
                msg = "连接容器错误，可能是传递的参数有问题！"
            print(msg)

        self.accept()

    def disconnect(self, close_code):
        self.conn_stream.write_stdin('exit\r')

    def receive(self, text_data):
        self.conn_stream.write_stdin(text_data)
```