# K8s 资源功能开发 - Deployment 资源
- 实现思路与 namespace\node\persistionvolume 资源一致，都是通过前端动态数据表格展示 + 后端 api 返回数据实现资源展示，只是通过浏览器缓存读取 namespace 数据用于返回指定命名空间下的 deployment 资源
### 实现资源的展示、搜索和删除
```python
# workload/views.py
@k8s.self_login_required
def deployment(request):
    return render(request, "workload/deployments.html")


@k8s.self_login_required
def deployment_api(request):
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    list = []
    k8s.laod_auth_config(auth_type=auth_type, token=token)
    app_api = client.AppsV1Api()

    if request.method == "GET":
        try:
            search_key = request.GET.get('search_key')
            current_namespace = request.GET.get("namespace")
            for dp in app_api.list_namespaced_deployment(current_namespace).items:
                name = dp.metadata.name
                namespace = dp.metadata.namespace
                replicas = dp.spec.replicas
                available_replicas = (dp.status.available_replicas if dp.status.available_replicas else 0)
                labels = dp.metadata.labels
                selector = dp.spec.selector.match_labels
                containers = {}
                for c in dp.spec.template.spec.containers:
                    containers[c.name] = c.image
                create_time = dp.metadata.creation_timestamp
                item = {"name": name, "namespace": namespace, "replicas":replicas, "available_replicas":available_replicas , "labels":labels, "selector":selector, "containers":containers, "create_time": create_time}
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
            app_api.delete_namespaced_deployment(name=name,namespace=current_namespace)
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
<!--template/workload/deployment.html-->
{% extends 'base.html' %}
{% block title %}Deployments{% endblock %}
{% block nav-item-2 %}layui-nav-itemed{% endblock %}
{% block nav-child-2-2 %}layui-this{% endblock %}
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

                <div class="layui-col-md12">
                    <table id="test" lay-filter="test"></table>
                    <script type="text/html" id="barDemo">
                        <a class="layui-btn layui-btn-xs layui-btn-primary" lay-event="yaml">YAML</a>
                        <a class="layui-btn layui-btn-danger layui-btn-xs" lay-event="del">删除</a>
                    </script>
                </div>
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
                , url: '{% url 'deployment_api' %}?namespace=' + namespace //数据接口
                , response: {
                    dataName: 'list'
                }
                , toolbar: '#toolbarDemo' //开启头部工具栏，并为其绑定左侧模板
                , defaultToolbar: ['filter', 'exports', 'print', { //自定义头部工具栏右侧图标。如无需自定义，去除该参数即可
                    title: '提示'
                    , layEvent: 'LAYTABLE_TIPS'
                    , icon: 'layui-icon-tips'
                }]
                , page: true //开启分页
                , cols: [[ //表头
                    {field: 'name', title: '名称', width: 200, sort: true}
                    , {field: 'namespace', title: '命名空间'}
                    , {field: 'replicas', title: '预期副本数'}
                    , {field: 'available_replicas', title: '可用副本数'}
                    , {field: 'labels', title: '标签', templet: labelsFormat}
                    , {field: 'selector', title: 'Pod标签选择器', templet: selecotrFormat}
                    , {field: 'containers', title: '容器', templet: containersFormat}
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
                        result += '<span>' + key + ':' + d.labels[key] + '</span><br>'
                    }
                    return result
                }
            }

            function selecotrFormat(d) {
                result = "";
                for (let key in d.selector) {
                    result += '<span>' + key + ':' + d.selector[key] + '</span><br>'
                }
                return result
            }

            function containersFormat(d) {
                result = "";
                for (let key in d.containers) {
                    result += '<span>' + key + ':' + d.containers[key] + '</span><br>'
                }
                return result
            }

            //监听行工具事件
            table.on('tool(test)', function (obj) {
                var data = obj.data;
                //console.log(obj)
                if (obj.event === 'del') {
                    layer.confirm('Are you sure to want delete the Deployment : ' + data.name + ' ?', function (index) {
                        var csrf_token = $('[name="csrfmiddlewaretoken"]').val();
                        var info = {'name': data.name, 'namespace': data.namespace}
                        $.ajax({
                            type: "DELETE",
                            url: "{% url 'deployment_api' %}",
                            data: info,
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
### 添加资源创建功能
```html
<!--template/workload/deployment_create.html-->
{% extends "base.html" %}
{% block title %}Deployments{% endblock %}
{% block nav-item-2 %}layui-nav-itemed{% endblock %}
{% block nav-child-2-1 %}layui-this{% endblock %}

{% block content %}
    {% csrf_token %}
    <div class="layui-card">
        <div class="layui-card-body">

            <fieldset class="layui-elem-field layui-field-title" style="margin-top: 20px;">
                <legend>创建 Deployment</legend>
            </fieldset>

            <form class="layui-form " onclick="return false">

                <div class="layui-form-item">
                    <label class="layui-form-label">名称：</label>
                    <div class="layui-input-block">
                        <input type="text" name="name" lay-verify="required" lay-reqtext="名称是必填项，不能为空！" placeholder=""
                               autocomplete="off" class="layui-input">
                    </div>
                </div>

                <div class="layui-form-item">
                    <label class="layui-form-label">命名空间：</label>
                    <div class="layui-input-block">
                        <select name="namespace" lay-verify="required" id="ns">
                        </select>
                    </div>
                </div>

                <div class="layui-form-item">
                    <label class="layui-form-label">镜像：</label>
                    <div class="layui-input-block">
                        <input type="text" name="image" lay-verify="required" lay-reqtext="镜像是必填项，不能为空！" placeholder=""
                               autocomplete="off" class="layui-input">
                    </div>
                </div>

                <div class="layui-form-item">
                    <label class="layui-form-label">副本数：</label>
                    <div class="layui-input-block">
                        <input type="text" name="replicas" value="3" autocomplete="off" class="layui-input">
                    </div>
                </div>

                <div class="layui-form-item">
                    <label class="layui-form-label">标签：</label>
                    <div class="layui-input-block">
                        <input type="text" name="labels" lay-verify="required" lay-reqtext="标签是必填项，不能为空！"
                               placeholder="示例: project=ms,app=gateway" autocomplete="off" class="layui-input">
                    </div>
                </div>

                <div class="layui-form-item">
                    <label class="layui-form-label">通用配置：</label>
                    <div class="layui-input-block">
                        <input type="radio" name="resources" value="1c2g" title="1核2G" checked="">
                        <input type="radio" name="resources" value="2c4g" title="2核4G">
                        <input type="radio" name="resources" title="自定义" disabled="">
                    </div>
                </div>

                <div class="layui-form-item">
                    <label class="layui-form-label">健康检查：</label>
                    <div class="layui-input-block">
                        <input type="checkbox" name="health[liveness]" title="存活检查">
                        <input type="checkbox" name="health[readiness]" title="就绪检查">
                    </div>
                </div>

                <div class="layui-form-item">
                    <div class="layui-input-block">
                        <button type="submit" class="layui-btn" lay-submit="" lay-filter="btn">立即提交</button>
                        <button type="reset" class="layui-btn layui-btn-primary">重置</button>
                    </div>
                </div>

            </form>

        </div>
    </div>
{% endblock %}

{% block ex_js %}
    <script>

        // 获取当前命名空间
        var storage = window.sessionStorage;
        var namespace = storage.getItem("namespace");

        layui.use(['table', 'form'], function () {
            var table = layui.table;
            var form = layui.form;
            var $ = layui.jquery;
            var csrf_token = $('[name="csrfmiddlewaretoken"]').val();

            //
            $("#ns").append('<option value=' + namespace + " selected>" + namespace + '</option>');
            //$("#ns").attr("disabled","disabled");
            form.render();  // 重新渲染，这个一定要放在最后这个位置

            //监听提交
            form.on('submit(btn)', function (data) {
                $.ajax({
                    url: '{% url "deployment_api" %}'
                    , type: 'POST'
                    , data: data.field
                    , headers: {'X-CSRFToken': csrf_token}
                    // 提交成功回调函数
                    , success: function (res) {
                        if (res.code == '0') {
                            layer.msg(res.msg, {icon: 6});
                        } else {
                            layer.msg(res.msg, {icon: 5})
                        }
                    }
                    // 访问接口失败函数
                    , error: function (res) {
                        layer.msg("服务器接口异常！", {icon: 5})
                    }
                })
            });

        });

    </script>
{% endblock %}
```
```python
@k8s.self_login_required
def deployment_api(request):
    """
    忽略不相干内容
    """
    elif request.method == "POST":
        name = request.POST.get("name", None)
        namespace = request.POST.get("namespace", None)
        image = request.POST.get("image", None)
        replicas = int(request.POST.get("replicas", None))
        print(namespace)
        labels = {}
        try:
            for l in request.POST.get("labels", None).split(","):
                k = l.split("=")[0]
                v = l.split("=")[1]
                labels[k] = v
        except Exception as e:
            res = {"code": 1, "msg": "标签格式错误！"}
            return JsonResponse(res)
        resources = request.POST.get("resources", None)
        health_liveness = request.POST.get("health[liveness]", None)
        health_readiness = request.POST.get("health[readiness]", None)
        if resources == "1c2g":
            resources = client.V1ResourceRequirements(
                limits={"cpu": "1", "memory": "2Gi"},
                requests={"cpu": "0.9", "memory": "0.9Gi"})
        elif resources == "2c4g":
            resources = client.V1ResourceRequirements(
                limits={"cpu": "2", "memory": "4Gi"},
                requests={"cpu": "1.9", "memory": "3.9Gi"})
        liveness_probe = ""
        if health_liveness == "on":
            liveness_probe = client.V1Probe(http_get="/", timeout_seconds=30, initial_delay_seconds=30)
        readiness_probe = ""
        if health_readiness == "on":
            readiness_probe = client.V1Probe(http_get="/", timeout_seconds=30, initial_delay_seconds=30)
        for dp in app_api.list_namespaced_deployment(namespace=namespace).items:
            if name == dp.metadata.name:
                res = {"code": 1, "msg": "Deployment已经存在！"}
                return JsonResponse(res)
        body = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(name=name),
            spec=client.V1DeploymentSpec(
                replicas=replicas,
                selector={'matchLabels': labels},
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(labels=labels),
                    spec=client.V1PodSpec(
                        containers=[client.V1Container(
                            # https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Container.md
                            name="web",
                            image=image,
                            env=[{"name": "TEST", "value": "123"}, {"name": "DEV", "value": "456"}],
                            ports=[client.V1ContainerPort(container_port=80)],
                            # liveness_probe=liveness_probe,
                            # readiness_probe=readiness_probe,
                            resources=resources,
                        )]
                    )
                ),
            )
        )
        try:
            app_api.create_namespaced_deployment(namespace=namespace, body=body)
            code = 0
            msg = "创建Deployment成功."
        except Exception as e:
            msg= str(e)
            code = 1
        result = {'code': code, 'msg': msg}
    return JsonResponse(result)
```
### 实现资源 yaml 格式的展示
- 使用 ACE 浏览器插件实现功能，sce 包放入 static 路径下
- 创建用于展示 yaml 信息的页面
```js
<!--template/workload/deployment.html-->
//监听行工具事件
layui.use('table', function () {
        table.on('tool(test)', function (obj) {
            var data = obj.data;
            //console.log(obj)
            if (obj.event === 'del') {
                //忽略内容
            // yaml 资源查看
            } else if (obj.event === 'yaml') {
                layer.open({
                    title: "YAML",
                    type: 2,
                    area: ["50%", "60%"],
                    content: '{% url 'ace_editor' %}?resource=deployment&namespace=' + data.namespace + '&name=' + data.name
                })
            }
        });
```
```python
# dashboard/views.py
# 使用 xframe_options_exempt 装饰器实现跨域
@xframe_options_exempt
@k8s.self_login_required
def export_resource_api(request):
    namespace = request.GET.get("namespace")
    resource = request.GET.get("resource")
    name = request.GET.get("name")

    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    k8s.laod_auth_config(auth_type=auth_type, token=token)

    core_api = client.CoreV1Api()  # namespace,pod,service,pv,pvc
    apps_api = client.AppsV1Api()  # deployment
    networking_api = client.NetworkingV1beta1Api()  # ingress
    storage_api = client.StorageV1Api()  # storage_class

    code = 0
    msg = "success!"
    if resource == "deployment":
        try:
            json_str = apps_api.read_namespaced_deployment(name=name, namespace=namespace,
                                                           _preload_content=False).read().decode()
            result = yaml.safe_dump(json.loads(json_str))
        except Exception as e:
            code = 1
            msg = str(e)
    res = {'code': code, 'msg': msg, 'data': result}
    return JsonResponse(res)

# 获取 deployment 页面提交的行信息并传入并跳转到 yaml 资源展示弹窗页面
@xframe_options_exempt
@k8s.self_login_required
def ace_editor(request):
    data = {}
    data["name"] = request.GET.get("name")
    data["namespace"] = request.GET.get("namespace")
    data["resource"] = request.GET.get("resource")
    print(data)
    return render(request, 'ace_editor.html', {'data': data})  # 传递给在线编辑器页面
```
```html
<!-- template/ace_editor.html -->
<link rel="stylesheet" href="/static/layui/css/layui.css">
<script src="/static/layui/layui.js"></script>

<script src="/static/ace/ace.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ace/theme/theme-chrome.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ace/mode/mode-yaml.js" type="text/javascript" charset="utf-8"></script>

<!--必须设置高度，否则无法显示-->
<div  id="code-editor" style="height: 98%;width:98%;"></div>

<script>
     //初始化对象
     var editor = ace.edit("code-editor");

     //设置编辑器样式，对应theme-*.js文件
     editor.setTheme("ace/theme/chrome");
     //设置代码语言，对应mode-*.js文件
     editor.session.setMode("ace/mode/yaml");
     //设置打印线是否显示
     editor.setShowPrintMargin(false);
     //字体大小
     editor.setFontSize(16);
     //设置只读（true时只读，用于展示代码）
     editor.setReadOnly(false);

     // 获取编辑内容
     /*
     editor.getSession().on("change", function () {
         var code = editor.getValue();
         console.log(code)
     }); */

    layui.use(['layer'], function(){
        var $ = layui.jquery;
        layer = layui.layer;  // 获取到使用的组件

        // 后端传：命名空间，资源，名称 。传过来的不是json对象，要转换
        var namespace = "{{ data.namespace }}";
        var resource = "{{ data.resource }}";
        var name = "{{ data.name }}";

        $.ajax({
           url: '{% url "export_resource_api" %}?' + 'namespace=' + namespace + '&resource=' + resource + "&name=" + name,
           type: 'GET',
           // 提交成功回调函数
           success: function (res) {
               if(res.code == '0') {
                   editor.setValue(res.data);   // 设置编辑内容
               } else {
                   layer.msg(res.msg, {icon: 5})
               }
           },
           // 访问接口失败函数
           error: function (res) {
               layer.msg("服务器接口异常！" , {icon:5})
           }
        })
    })

</script>
```
### 实现资源详情的查看
- 需要具备 deployment 资源的怕基本信息，容器信息，service\ingress 信息，还要有历史版本 ReplicaSet 信息
```js
//deployments.html
//监听行工具事件
table.on('tool(test)', function (obj) {
    var data = obj.data;
    //console.log(obj)
    if (obj.event === 'del') {
        // 忽略内容
    } else if (obj.event === 'yaml') {
        // 忽略内容
    }else if (obj.event === "details") {
        window.location.href = "{%  url 'deployment_details' %}?namespace=" + data.namespace + "&name=" + data.name
    }
});

//deployment_details.html
{% extends "base.html" %}
{% block title %}Deployments{% endblock %}
{% block nav-item-2 %}layui-nav-itemed{% endblock %}
{% block nav-child-2-2 %}layui-this{% endblock %}

{% block content %}
    {% csrf_token %}
    <style>
        .layui-card-header {
            font-size: 16px;
        }

        .layui-card-body {
            font-size: 16px;
            padding: 10px;
        }

        .layui-card-body .layui-inline {
            padding: 10px;
            font-size: 14px;
            width: 98%;
            color: #646464;
            border: 1px solid #ebeef5;
            border-radius: 4px;
        }

        #result {
            background-color: #fff;
            border: 1px solid #ebeef5;
            border-radius: 4px;
            box-shadow: 0 1px 1px 0 #c2c2c2;
            padding: 10px;
            font-size: 14px;
        }

        /* span徽章 */
        .layui-badge {
            font-size: 14px;
        }

        .svc-ing {
            margin: 10px;
            line-height: 32px;
        }

        .svc-ing table {
            width: 100%;
            text-align: center
        }

        .svc-ing table th {
            background-color: #d5dce7;
            color: #2e5085;
        }

        .svc-ing table td, tr {
            border: 1px solid #ebeef5;
            font-size: 15px;
        }

        .self-none {
            background-color: #f4f4f5;
            color: #909399;
            padding: 5px;
            font-size: 14px;
        }
    </style>
    <div class="layui-row layui-col-space10">
        <div class="layui-col-md6 layui-col-space10">
            <div class="layui-col-md12">
                <div class="layui-card">
                    <div class="layui-card-header">基本信息</div>
                    <div class="layui-card-body">
                        名称：{{ dp_info.name }}
                        <hr class="layui-bg-gray">
                        命名空间：{{ dp_info.namespace }}
                        <hr class="layui-bg-gray">
                        副本数量：<span
                            class="layui-badge layui-bg-green">期望 {{ dp_info.replicas }} / 可用 {{ dp_info.available_replicas }}</span>
                        <hr class="layui-bg-gray">
                        镜像：
                        {% for c in dp_info.containers %}
                            {% if dp_info.containers|length == 1 %}
                                <span>{{ c.image }}</span>
                            {% else %}
                                <span style='border: 1px solid #d6e5ec;padding: 3px'>{{ c.image }}</span>
                            {% endif %}
                        {% endfor %}
                        <hr class="layui-bg-gray">
                        标签选择器：
                        {% for k,v in dp_info.selector.items %}
                            <span style='border: 1px solid #d6e5ec;border-radius: 20px;padding: 1px 6px 1px 6px'>{{ k }}={{ v }}</span>
                        {% endfor %}
                        <hr class="layui-bg-gray">
                        创建时间：{{ dp_info.create_time }}
                        <hr class="layui-bg-gray">
                    </div>
                </div>
            </div>
            <div class="layui-col-md12">
                <div class="layui-card">
                    <div class="layui-card-header">Service</div>
                    <div class="layui-card-body">
                        <div class="svc-ing">
                            {% if dp_info.service %}
                                {% for svc in dp_info.service %}
                                    <p>
                                        类型：{{ svc.type }}<br>
                                        ClusterIP：{{ svc.cluster_ip }}&ensp;&ensp;<span
                                            class="layui-badge layui-bg-green"
                                            style="font-size: 12px">集群内部访问地址</span><br>
                                        访问端口：<br>
                                    </p>
                                    <table>
                                        <thead style="">
                                        <tr>
                                            <th>名称</th>
                                            <th>服务端口</th>
                                            <th>容器端口</th>
                                            <th>协议</th>
                                            {% if svc.type == "NodePort" %}
                                                <th>NodePort</th>
                                            {% endif %}
                                        </tr>
                                        </thead>

                                        <tbody>
                                        {% for k in svc.ports %}
                                            <tr>
                                                <td>{{ k.name }}</td>
                                                <td>{{ k.port }}</td>
                                                <td>{{ k.target_port }}</td>
                                                <td>{{ k.protocol }}</td>
                                                {% if svc.type == "NodePort" %}
                                                    <td>{{ k.node_port }}</td>
                                                {% endif %}
                                            </tr>
                                        {% endfor %}
                                        </tbody>
                                    </table>
                                {% endfor %}
                            {% else %}
                                <span class="self-none">此处显示通过 Deployment 标签筛选出的Service，但是您并未定义！</span>
                                <br><br>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>
            <div class="layui-col-md12">
                <div class="layui-card">
                    <div class="layui-card-header">Ingress</div>
                    <div class="layui-card-body">
                        <div class="svc-ing">
                            {% if dp_info.ingress.rules %}
                                {% for ing in dp_info.ingress.rules %}
                                    <p>
                                        {% if dp_info.ingress.tls == None %}
                                            域名：<a href="http://{{ ing.host }}" target="_blank" style="color: #007af5">http://{{ ing.host }}</a>
                                        {% else %}
                                            域名：<a href="https://{{ ing.host }}" target="_blank" style="color: #007af5">https://{{ ing.host }}</a>
                                        {% endif %}
                                    </p>
                                    <table>
                                        <thead style="">
                                        <tr>
                                            <th>路由规则</th>
                                            <th>服务名称</th>
                                            <th>服务端口</th>
                                            <th>HTTPS</th>
                                        </tr>
                                        </thead>

                                        <tbody>
                                        <tr>
                                            {% if ing.http.path == None %}
                                                <td>/</td>
                                            {% else %}
                                                <td>{{ ing.http.path }}</td>
                                            {% endif %}

                                            {% for h in ing.http.paths %}
                                                <td>{{ h.backend.service_name }}</td>
                                                <td>{{ h.backend.service_port }}</td>
                                            {% endfor %}

                                            {% if dp_info.ingress.tls != None %}
                                                {% for t in dp_info.ingress.tls %}
                                                    <td>
                                                        {% for i in t.hosts %}
                                                            域名：{{ i }}<br>
                                                        {% endfor %}
                                                        证书：{{ t.secret_name }}
                                                    </td>
                                                {% endfor %}
                                            {% else %}
                                                <td>未启用</td>
                                            {% endif %}
                                        </tr>
                                        </tbody>
                                    </table>
                                {% endfor %}
                            {% else %}
                                <span class="self-none">此处显示是通过 Ingress 后端与上面 Service 匹配的 Ingress，但是您并未定义！</span>
                                <br><br>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="layui-col-md6">
            <div class="layui-card">
                <div class="layui-card-header">更多信息</div>
                <div class="layui-card-body">
                    滚动更新：
                    <div class="layui-inline" style="width: 30%">
                        最大超出副本数：{{ dp_info.rolling_update.max_surge }}<br>
                        最大不可用副本数：{{ dp_info.rolling_update.max_unavailable }}
                    </div>

                    <hr class="layui-bg-gray">
                    数据卷：
                    {% if  dp_info.volumes|length > 0 %}
                        <div class="layui-inline" id="inline">
                            <div class="layui-row layui-col-space15">
                                {% for vol in dp_info.volumes %}
                                    <div class="layui-col-md4">
                                        <div class="grid-demo grid-demo-bg1">

                                            {% for k,v in vol.items %}

                                                <div id="result">
                                                    卷名称：{{ v.name }}<br>
                                                    卷类型：{{ k }}<br>
                                                </div>
                                            {% endfor %}
                                        </div>
                                    </div>
                                {% endfor %}

                            </div>
                        </div>
                    {% else %}
                        <span class="self-none">None</span>
                    {% endif %}

                    <hr class="layui-bg-gray">
                    污点容忍：
                    {% if  dp_info.tolerations|length > 0 %}
                        <div class="layui-inline">
                            <div class="layui-row layui-col-space15">
                                {% for t in dp_info.tolerations %}
                                    <div class="layui-col-md4">
                                        <div class="grid-demo grid-demo-bg1">
                                            <div class="layui-card">
                                                <div class="layui-card-body" style="font-size: 14px">
                                                    key：{{ t.key }}<br>
                                                    operator：{{ t.operator }}<br>
                                                    effect：{{ t.effect }}<br>
                                                    容忍时间：{{ t.toleration_seconds }}<br>
                                                </div>
                                            </div>

                                        </div>
                                    </div>
                                {% endfor %}
                            </div>
                        </div>
                    {% else %}
                        <span class="self-none">None</span>
                    {% endif %}

                    <hr class="layui-bg-gray">
                    容器配置：
                    <div class="layui-inline">
                        <div class="layui-row layui-col-space15" style="height: 480px;overflow: auto">
                            {% for c in dp_info.containers %}
                                <div class="layui-col-md5">
                                    <div class="grid-demo grid-demo-bg1">
                                        <div class="layui-card">
                                            <div class="layui-card-body">

                                                <span style="color: #fff;border-radius: 4px;background-color: #2e5085;padding: 2px;">容器{{ forloop.counter }}：{{ c.name }}</span><br><br>

                                                {% if c.env != None %}
                                                    <div id="result">
                                                        <span class="layui-badge layui-bg-green">变量</span>
                                                        <hr>
                                                        {% for v in c.env %}

                                                            {% if v.value != None %}
                                                                来源：自定义<br>
                                                                名称：{{ v.name }}<br>
                                                                值：{{ v.value }}
                                                            {% elif v.value_from != None %}
                                                                {% if v.value_from.config_map_key_ref != None %}
                                                                    来源：configmap /
                                                                    {{ v.value_from.config_map_key_ref.name }} /
                                                                    {{ v.value_from.config_map_key_ref.key }}<br>
                                                                    名称：{{ v.name }}
                                                                {% elif v.value_from.secret_key_ref != None %}
                                                                    来源：secret / {{ v.value_from.secret_key_ref.name }} /
                                                                    {{ v.value_from.secret_key_ref.key }}<br>
                                                                    名称：{{ v.name }}
                                                                {% elif v.value_from.field_ref != None %}
                                                                    来源：Pod属性 / {{ v.value_from.field_ref.field_path }}
                                                                    <br>
                                                                    名称：{{ v.name }}
                                                                {% endif %}
                                                            {% endif %}
                                                            {% if forloop.counter != c.env|length %}
                                                                <hr>
                                                            {% endif %}
                                                        {% endfor %}

                                                    </div>
                                                {% else %}
                                                    <div id="result">
                                                        <span class="layui-badge layui-bg-green">变量</span>
                                                        <hr>
                                                        <span class="self-none">None</span>
                                                    </div>
                                                {% endif %}
                                                <br>

                                                {% if c.ports != None %}
                                                    <div id="result">
                                                        <span class="layui-badge layui-bg-green">端口</span>
                                                        <hr>
                                                        {% for p in c.ports %}
                                                            名称：{{ p.name }}<br>
                                                            容器端口：{{ p.container_port }}<br>
                                                            协议：{{ p.protocol }}
                                                        {% endfor %}
                                                    </div>
                                                {% else %}
                                                    <div id="result">
                                                        <span class="layui-badge layui-bg-green">端口</span>
                                                        <hr>
                                                        <span class="self-none">None</span>
                                                    </div>
                                                {% endif %}

                                                <br>

                                                {% if c.resources.requests == None and c.resources.limits == None %}
                                                    <div id="result">
                                                        <span class="layui-badge layui-bg-green">资源分配</span>
                                                        <hr>
                                                        <span class="self-none">None</span>
                                                    </div>
                                                {% else %}
                                                    <div id="result">
                                                        <span class="layui-badge layui-bg-green">资源分配</span>
                                                        <hr>
                                                        {% if c.resources.requests != None %}
                                                            <span class="layui-badge layui-bg-orange">请求</span><br>
                                                            {% if c.resources.requests.cpu != None %}
                                                                CPU：{{ c.resources.requests.cpu }}<br>
                                                            {% else %}
                                                                CPU: <span class="layui-badge layui-bg-gray">None</span>
                                                            {% endif %}
                                                            {% if c.resources.requests.memory != None %}
                                                                内存：{{ c.resources.requests.memory }}<br>
                                                            {% else %}
                                                                内存: <span class="layui-badge layui-bg-gray">None</span>
                                                            {% endif %}
                                                        {% else %}
                                                            <span class="layui-badge layui-bg-orange">请求</span>&ensp;
                                                            <span class="self-none">None</span>
                                                        {% endif %}

                                                        <hr>

                                                        {% if c.resources.limits != None %}
                                                            <span class="layui-badge layui-bg-orange">限制</span><br>
                                                            {% if c.resources.limits.cpu != None %}
                                                                CPU：{{ c.resources.limits.cpu }}<br>
                                                            {% else %}
                                                                CPU: <span class="layui-badge layui-bg-gray">None</span>
                                                            {% endif %}
                                                            {% if c.resources.limits.memory != None %}
                                                                内存：{{ c.resources.limits.memory }}<br>
                                                            {% else %}
                                                                内存: <span class="layui-badge layui-bg-gray">None</span>
                                                            {% endif %}
                                                        {% else %}
                                                            <span class="layui-badge layui-bg-orange">限制</span>&ensp;
                                                            <span class="self-none">None</span>
                                                        {% endif %}
                                                    </div>
                                                {% endif %}

                                                <br>

                                                {% if c.readiness_probe == None and c.liveness_probe == None %}
                                                    <div id="result">
                                                        <span class="layui-badge layui-bg-green">健康检查</span>
                                                        <hr>
                                                        <span class="self-none">None</span>
                                                    </div>
                                                {% else %}
                                                    <div id="result">
                                                        <span class="layui-badge layui-bg-green">健康检查</span>
                                                        <hr>
                                                        {% if c.readiness_probe != None %}
                                                            <span class="layui-badge layui-bg-orange">就绪检查</span><br>
                                                            {% if c.readiness_probe.tcp_socket != None %}
                                                                类型：tcp_socket<br>
                                                                端口：{{ c.readiness_probe.tcp_socket.port }}<br>
                                                                初始延迟检查时间(s)：
                                                                {{ c.readiness_probe.initial_delay_seconds }}<br>
                                                                周期间隔(s)：{{ c.readiness_probe.period_seconds }}
                                                            {% elif c.readiness_probe.http_get  != None %}
                                                                类型：http_get<br>
                                                                URL：{{ c.readiness_probe.http_get.path }}<br>
                                                                端口：{{ c.readiness_probe.http_get.port }}<br>
                                                                协议：{{ c.readiness_probe.http_get.scheme }}<br>
                                                                初始延迟检查时间(s)：
                                                                {{ c.readiness_probe.initial_delay_seconds }}<br>
                                                                周期间隔(s)：{{ c.readiness_probe.period_seconds }}
                                                                {#                                    {% elif c.readiness_probe._exec  != None %}#}
                                                                {#                                        {{ c.readiness_probe._exec }}#}
                                                            {% endif %}
                                                        {% else %}
                                                            <span class="layui-badge layui-bg-orange">就绪检查</span>&ensp;
                                                            <span class="self-none">None</span>
                                                        {% endif %}

                                                        <hr>

                                                        {% if c.liveness_probe != None %}
                                                            <span class="layui-badge layui-bg-orange">存活检查</span><br>
                                                            {% if c.liveness_probe.tcp_socket != None %}
                                                                类型：tcp_socket<br>
                                                                端口：{{ c.liveness_probe.tcp_socket.port }}<br>
                                                                初始延迟检查时间(s)：
                                                                {{ c.readiness_probe.initial_delay_seconds }}<br>
                                                                周期间隔(s)：{{ c.readiness_probe.period_seconds }}
                                                            {% elif c.liveness_probe.http_get  != None %}
                                                                类型：http_get<br>
                                                                URL：{{ c.liveness_probe.http_get.path }}<br>
                                                                端口：{{ c.liveness_probe.http_get.port }}<br>
                                                                协议：{{ c.liveness_probe.http_get.scheme }}<br>
                                                                初始延迟检查时间(s)：{{ c.liveness_probe.initial_delay_seconds }}
                                                                <br>
                                                                周期间隔(s)：{{ c.liveness_probe.period_seconds }}
                                                                {#                                    {% elif c.readiness_probe._exec  != None %}#}
                                                                {#                                        {{ c.readiness_probe._exec }}#}
                                                            {% endif %}
                                                        {% else %}
                                                            <span class="layui-badge layui-bg-orange">存活检查</span>&ensp;
                                                            <span class="self-none">None</span>
                                                        {% endif %}
                                                    </div>
                                                {% endif %}

                                                <br>

                                                {% if  c.volume_mounts != None %}
                                                    <div id="result">
                                                        <span class="layui-badge layui-bg-green">数据卷</span>
                                                        <hr>
                                                        {% for vol in c.volume_mounts %}
                                                            名称：{{ vol.name }}<br>
                                                            挂载点：{{ vol.mount_path }}<br>
                                                            子路径：{{ vol.sub_path }}<br>
                                                            只读：{{ vol.read_only }}

                                                            {#                                  {% for k,v in vol.items %}#}
                                                            {#                                  数据卷：{{ k }}{{ v }}#}
                                                            {#                                  {% endfor %}#}
                                                        {% endfor %}
                                                    </div>
                                                {% else %}
                                                    <div id="result">
                                                        <span class="layui-badge layui-bg-green">数据卷</span>
                                                        <hr>
                                                        <span class="self-none">None</span>
                                                    </div>
                                                {% endif %}

                                            </div>
                                        </div>
                                    </div>
                                </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>

        </div>
        <div class="layui-col-md12">
            <div class="layui-card">
                <div class="layui-card-header">历史发布版本（ReplicaSet副本集）&ensp;&ensp;
                    <span class="layui-badge layui-bg-green" style="font-size: 12px">  最大历史版本数量：{{ dp_info.rs_number }}</span>
                </div>
                <div class="layui-card-body">
                    <table class="layui-hide" id="test" lay-filter="test"></table>
                </div>
            </div>
            <script type="text/html" id="barDemo">
                <a class="layui-btn layui-btn-primary layui-btn-xs" lay-event="yaml">YAML</a>
                <a class="layui-btn layui-btn-xs" lay-event="rollback">回滚</a>
            </script>
        </div>
    </div>

{% endblock %}

{% block ex_js %}
    <script>

        layui.use('table', function () {
            var table = layui.table;
            var $ = layui.jquery;
            var csrf_token = $('[name="csrfmiddlewaretoken"]').val();

            table.render({
                elem: '#test'
                , url: '{% url "replicaset_api" %}?namespace={{ namespace }}&name={{ dp_name }}'
                , page: false  // 关闭分页
                , cols: [[
                    {field: 'name', title: '名称', sort: true}
                    {#,{field: 'namespace', title: '命名空间', sort: true}#}
                    , {field: 'replicas', title: '期望', sort: true}
                    , {field: 'ready_replicas', title: '就绪'}
                    , {field: 'available_replicas', title: '可用', sort: true}
                    , {field: 'create_time', title: '创建时间'}
                    , {field: 'revision', title: '版本号', sort: true}
                    , {field: 'containers', title: '镜像版本差异', templet: containersFormat}
                    , {fixed: 'right', title: '操作', toolbar: '#barDemo'}
                ]]
            });

            function containersFormat(d) {
                result = "";
                for (let key in d.containers) {
                    result += key + '=' + d.containers[key] + '<br>'
                }
                return result
            }

            //监听行工具事件
            table.on('tool(test)', function (obj) {
                var data = obj.data;
                if (obj.event === 'rollback') {
                    layer.confirm('真的要回滚到 ' + data["name"] + "/" + data["revision"] + ' 这个版本吗？', function (index) {
                        var info = {'dp_name': '{{ dp_name }}', 'namespace': '{{ namespace }}', 'reversion': data["revision"]}
                        $.ajax({
                            url: '{% url "replicaset_api" %}',
                            type: "POST",
                            data: info,
                            headers: {'X-CSRFToken': csrf_token},
                            success: function (res) {
                                if (res.code == '0') {
                                    layer.msg(res.msg, {icon: 6});
                                } else {
                                    layer.msg(res.msg, {icon: 5})
                                }
                            }
                            , error: function () {
                                layer.open({
                                    type: 0,
                                    title: ['异常信息'],
                                    content: "服务器接口异常！"
                                })
                            }
                        });
                    })
                } else if (obj.event === 'yaml') {
                    layer.open({
                        title: "YAML",
                        type: 2,  // 加载层，从另一个网址引用
                        area: ['50%', '60%'],
                        content: '{% url "ace_editor" %}?resource=replicaset&namespace=' + data["namespace"] + "&name=" + data["name"],
                    });
                }
            });

        });

    </script>
{% endblock %}
```
```python
# workload/views.py
@k8s.self_login_required
def deployment_details(request):
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    k8s.laod_auth_config(auth_type=auth_type,token=token)
    core_api = client.CoreV1Api()
    apps_api = client.AppsV1Api()
    networking_api = client.NetworkingV1beta1Api()

    dp_name = request.GET.get("name")
    namespace = request.GET.get("namespace")

    dp_info = []
    for dp in apps_api.list_namespaced_deployment(namespace=namespace).items:
        if dp_name == dp.metadata.name:
            name = dp.metadata.name
            namespace = dp.metadata.namespace
            replicas = dp.spec.replicas
            available_replicas = (
                0 if dp.status.available_replicas is None else dp.status.available_replicas)  # ready_replicas
            labels = dp.metadata.labels
            selector = dp.spec.selector.match_labels

            # 通过deployment反查对应service
            service = []
            svc_name = None
            for svc in core_api.list_namespaced_service(namespace=namespace).items:
                if svc.spec.selector == selector:
                    svc_name = svc.metadata.name  # 通过该名称筛选ingress
                    type = svc.spec.type
                    cluster_ip = svc.spec.cluster_ip
                    ports = svc.spec.ports

                    data = {"type": type, "cluster_ip": cluster_ip, "ports": ports}
                    service.append(data)

            # service没有创建，ingress也就没有  ingress->service->deployment->pod
            ingress = {"rules": None, "tls": None}
            for ing in networking_api.list_namespaced_ingress(namespace=namespace).items:
                for r in ing.spec.rules:
                    for b in r.http.paths:
                        if b.backend.service_name == svc_name:
                            ingress["rules"] = ing.spec.rules
                            ingress["tls"] = ing.spec.tls

            containers = []
            for c in dp.spec.template.spec.containers:
                c_name = c.name
                image = c.image
                liveness_probe = c.liveness_probe
                readiness_probe = c.readiness_probe
                resources = c.resources  # 在前端处理
                env = c.env
                ports = c.ports
                volume_mounts = c.volume_mounts
                args = c.args
                command = c.command

                container = {"name": c_name, "image": image, "liveness_probe": liveness_probe,
                             "readiness_probe": readiness_probe,
                             "resources": resources, "env": env, "ports": ports,
                             "volume_mounts": volume_mounts, "args": args, "command": command}
                containers.append(container)

            tolerations = dp.spec.template.spec.tolerations
            rolling_update = dp.spec.strategy.rolling_update
            volumes = []
            if dp.spec.template.spec.volumes is not None:
                for v in dp.spec.template.spec.volumes:  # 返回类似字典格式，不知道为啥不能遍历
                    volume = {}
                    if v.config_map is not None:
                        volume["config_map"] = v.config_map
                    elif v.secret is not None:
                        volume["secret"] = v.secret
                    elif v.empty_dir is not None:
                        volume["empty_dir"] = v.empty_dir
                    elif v.host_path is not None:
                        volume["host_path"] = v.host_path
                    elif v.config_map is not None:
                        volume["downward_api"] = v.downward_api
                    elif v.config_map is not None:
                        volume["glusterfs"] = v.glusterfs
                    elif v.cephfs is not None:
                        volume["cephfs"] = v.cephfs
                    elif v.rbd is not None:
                        volume["rbd"] = v.rbd
                    elif v.persistent_volume_claim is not None:
                        volume["persistent_volume_claim"] = v.persistent_volume_claim
                    else:
                        volume["unknown"] = "unknown"
                    volumes.append(volume)

            rs_number = dp.spec.revision_history_limit
            create_time = k8s.dt_format(dp.metadata.creation_timestamp)

            dp_info = {"name": name, "namespace": namespace, "replicas": replicas,
                       "available_replicas": available_replicas, "labels": labels,
                       "selector": selector, "containers": containers, "rs_number": rs_number,
                       "rolling_update": rolling_update, "create_time": create_time, "volumes": volumes,
                       "tolerations": tolerations, "service": service, "ingress": ingress}

    return render(request, 'workload/deployment_details.html',
                  {'dp_name': dp_name, 'namespace': namespace, 'dp_info': dp_info})


@k8s.self_login_required
def replicaset_api(request):
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    k8s.load_auth_config(auth_type, token)
    apps_api = client.AppsV1Api()
    apps_beta_api = client.ExtensionsV1beta1Api()

    if request.method == "GET":
        dp_name = request.GET.get("name", None)
        namespace = request.GET.get("namespace", None)
        data = []
        for rs in apps_api.list_namespaced_replica_set(namespace=namespace).items:
            current_dp_name = rs.metadata.owner_references[0].name
            rs_name = rs.metadata.name
            if dp_name == current_dp_name:
                namespace = rs.metadata.namespace
                replicas = rs.status.replicas
                available_replicas = rs.status.available_replicas
                ready_replicas = rs.status.ready_replicas
                revision = rs.metadata.annotations["deployment.kubernetes.io/revision"]
                create_time = rs.metadata.creation_timestamp

                containers = {}
                for c in rs.spec.template.spec.containers:
                    containers[c.name] = c.image

                rs = {"name": rs_name, "namespace": namespace, "replicas": replicas,
                      "available_replicas": available_replicas, "ready_replicas": ready_replicas,
                      "revision": revision, 'containers': containers, "create_time": create_time}
                data.append(rs)
        count = len(data)  # 可选，rs默认保存10条，所以不用分页
        res = {"code": 0, "msg": "", "count": count, 'data': data}
    elif request.method == "POST":
        res = {"code": 1, "msg": "代码调试中，等待完成"}
    return JsonResponse(res)
```
### 实现 deployment 资源的扩容和缩容
```python
# workload/views.py
@k8s.self_login_required
def deployment_api(request):
    """
    忽略其他内容
    """
    elif request.method == "PUT":
        # 更新
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        namespace = request_data.get("namespace")
        replicas = int(request_data.get("replicas"))
        try:
            body = app_api.read_namespaced_deployment(name=name, namespace=namespace)
            current_replicas = body.spec.replicas
            min_replicas = 0
            max_replicas = 20
            if replicas > current_replicas and replicas < max_replicas:
                # body = body.spec.template.spec.containers[0].image = "nginx:1.17"
                body.spec.replicas = replicas  # 更新对象内副本值
                app_api.patch_namespaced_deployment(name=name, namespace=namespace, body=body)
                msg = "扩容成功！"
                code = 0
            elif replicas < current_replicas and replicas > min_replicas:
                body.spec.replicas = replicas
                app_api.patch_namespaced_deployment(name=name, namespace=namespace, body=body)
                msg = "缩容成功！"
                code = 0
            elif replicas == current_replicas:
                msg = "副本数一致！"
                code = 1
            elif replicas > max_replicas:
                msg = "副本数设置过大！请联系管理员操作。"
                code = 1
            elif replicas == min_replicas:
                msg = "副本数不能设置0！"
                code = 1
        except Exception as e:
            msg = str(e)
            code = 1
        result = {"code": code, "msg": msg}
```
```js
// template/deployments.html
table.on('tool(test)', function (obj) {
    var data = obj.data;
    //console.log(obj)
    if (obj.event === 'del') {
        //
    } else if (obj.event === 'yaml') {
        //
    } else if (obj.event === "details") {
        //
    } else if (obj.event === "scale") {
        layer.prompt({
            formType: 0
            , title: "扩容/缩容（副本数）"
            , value: data.replicas
        }, function (value, index) {
            data['replicas'] = value
            $.ajax({
                type: "PUT",
                url: "{% url 'deployment_api' %}",
                data: data,
                headers: {'X-CSRFToken': csrf_token},
                success: function (res) {
                    if (res.code == 0) {
                        layer.msg(res.msg, {icon: 6, time: 6000}) // 默认停顿3秒
                        obj.update({
                            replicas: value
                        })
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
            layer.close(index)
        });
    }
});
```