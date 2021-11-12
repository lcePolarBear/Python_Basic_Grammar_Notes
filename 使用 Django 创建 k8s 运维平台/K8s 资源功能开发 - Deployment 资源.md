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