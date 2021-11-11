# K8s 资源功能开发 - PersistentVolume 资源
- 实现思路与 namespace\node 资源一致，都是通过前端动态数据表格展示 + 后端 api 返回数据实现资源展示
```python
# k8s/views.py
@k8s.self_login_required
def pv(request):
    return render(request, "k8s/pv.html")

@k8s.self_login_required
def pv_api(request):
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    list = []
    k8s.laod_auth_config(auth_type=auth_type, token=token)
    core_api = client.CoreV1Api()

    if request.method == "GET":
        try:
            search_key = request.GET.get('search_key')
            for pv in core_api.list_persistent_volume().items:
                name = pv.metadata.name
                capacity = pv.spec.capacity["storage"]
                access_modes = pv.spec.access_modes
                reclaim_policy = pv.spec.persistent_volume_reclaim_policy
                status = pv.status.phase
                if pv.spec.claim_ref is not None:
                    pvc_ns = pv.spec.claim_ref.namespace
                    pvc_name = pv.spec.claim_ref.name
                    pvc = "%s / %s" % (pvc_ns, pvc_name)
                else:
                    pvc = "未绑定"
                storage_class = (pv.spec.storage_class_name if pv.spec.storage_class_name else "None")
                create_time = pv.metadata.creation_timestamp
                item = {"name": name, "capacity": capacity, "access_modes":access_modes, "reclaim_policy":reclaim_policy , "status":status, "pvc":pvc, "storage_class":storage_class,"create_time": create_time}
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

    elif request.method == "DELETE":
        request_date = QueryDict(request.body)
        pv = request_date.get("pv")
        try:
            core_api.delete_persistent_volume(name=pv)
            code = 0
            msg = "delete operation success!"
        except Exception as e:
            code = 1
            msg = "删除失败"
        result = {'code': code, 'msg': msg}
    return JsonResponse(result)
```
```html
<!-- template/k8s/node.html -->
{% extends 'base.html' %}
{% block title %}PersistentVolumes{% endblock %}
{% block nav-item-1 %}layui-nav-itemed{% endblock %}
{% block nav-child-1-3 %}layui-this{% endblock %}
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
    </div>
{% endblock %}
{% block ex_js %}
<script>
layui.use('table', function(){
    var table = layui.table;
    var $ = layui.jquery;
    var csrf_token = $('[name="csrfmiddlewaretoken"]').val();
    //动态渲染表格
    table.render({
        elem: '#test'
        ,response: {
            dataName: 'list'
        }
      ,url: '{% url 'pv_api' %}' //数据接口
      //,toolbar: '#toolbarDemo' //开启头部工具栏，并为其绑定左侧模板
      ,page: true //开启分页
      ,cols: [[ //表头
          {field: 'name', title: '名称', sort: true}
          ,{field: 'capacity', title: '容量'}
          ,{field: 'access_modes', title: '访问模式'}
          ,{field: 'reclaim_policy', title: '回收策略'}
          ,{field: 'status', title: '状态'}
          ,{field: 'pvc', title: 'PVC(命名空间/名称)'}
          ,{field: 'storage_class', title: '存储类'}
          ,{field: 'create_time', title: '创建时间'}
          ,{fixed: 'right', title:'操作', toolbar: '#barDemo', width:150}
      ]]
      ,id: "TT"
    });
    // 标签格式化
        function labelsFormat(d) {
            result = "";
            if (d.labels == null) {
                return "None"
            } else {
                for(let key in d.labels) {
                    result += '<span style="border: 1px solid #009688;border-radius: 5px">' + key + ':' + d.labels[key] + '</span><br>'
                }
                console.log(result);
                return result
            }
        }
    //监听行工具事件
    table.on('tool(test)', function(obj){
        var data = obj.data;
        //console.log(obj)
        if(obj.event === 'del'){
        layer.confirm('Are you sure to want delete the ' + data.name + ' ?', function(index){
            var info = {'pv': data.name};
            $.ajax({
                type: "DELETE",
                url: "{% url 'pv_api' %}",
                data: info,
                headers: {'X-CSRFToken': csrf_token},
                success: function (res) {
                    if(res.code == 0){
                        obj.del();  // 删除当前页面数据
                        layer.msg(res.msg,{icon: 6, time: 6000}) // 默认停顿3秒
                    } else {
                        layer.msg(res.msg,{icon: 5})
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
        } else if(obj.event === 'yaml'){
            // 查看YAML
        }
    });
    // 监控搜索事件
    $('#searchBtn').click(function(){
        var search_key = $('input[name="name"]').val();
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
# pv 创建功能
```html
<!--k8s/pv_create.html-->
{% extends "base.html" %}
{% block title %}PersistentVolumes{% endblock %}
{% block nav-item-1 %}layui-nav-itemed{% endblock %}
{% block nav-child-1-3 %}layui-this{% endblock %}

{% block content %}
    {% csrf_token %}
    <div class="layui-card">
        <div class="layui-card-body">

            <fieldset class="layui-elem-field layui-field-title" style="margin-top: 20px;">
                <legend>创建 PersistentVolume</legend>
            </fieldset>

            <form class="layui-form " onclick="return false">
                <div class="layui-form-item">
                    <label class="layui-form-label">名称：</label>
                    <div class="layui-input-block">
                        <input type="text" name="name" lay-verify="required" lay-reqtext="名称是必填项，不能为空！" placeholder=""
                               autocomplete="off" class="layui-input">
                    </div>
                </div>

                <div class="layui-form-item" pane="">
                    <label class="layui-form-label">存储容量：</label>
                    <div class="layui-input-block">
                        <input type="radio" name="capacity" value="1Gi" title="1Gi" checked="">
                        <input type="radio" name="capacity" value="5Gi" title="5Gi">
                        <input type="radio" name="capacity" value="10Gi" title="10Gi">
                        <input type="radio" name="capacity" value="20Gi" title="20Gi">
                        <input type="radio" name="capacity" title="自定义" disabled="">
                    </div>
                </div>

                <div class="layui-form-item">
                    <label class="layui-form-label">访问模式：</label>
                    <div class="layui-input-block">
                        <input type="radio" name="access_mode" value="ReadWriteMany" title="多节点读写" checked="">
                        <input type="radio" name="access_mode" value="ReadOnlyMany" title="多节点只读">
                        <input type="radio" name="access_mode" value="ReadWriteOnce" title="单节点读写">
                    </div>
                </div>

                <div class="layui-form-item">
                    <label class="layui-form-label">存储类型：</label>
                    <div class="layui-input-inline">
                        <select name="storage_class">
                            <option value=""></option>
                            <optgroup label="单点存储(适合非核心业务)">
                                <option value="nfs">NFS</option>
                            </optgroup>
                            <optgroup label="分布式存储(暂不支持)">
                                <option value="cephfs">CephFS</option>
                                <option value="cephrbd">CephRBD</option>
                            </optgroup>
                        </select>
                    </div>
                </div>

                <div class="layui-form-item" style="padding-left: 30px">
                    <label class="layui-form-label">服务器IP：</label>
                    <div class="layui-input-block">
                        <select name="server_ip" lay-verify="required" lay-search="" lay-filter="select_ns2">
                            <option value="">直接选择或搜索选择</option>
                            <option value="192.168.31.62">192.168.102.112</option>
                        </select>
                    </div>
                    <label class="layui-form-label">挂载路径：</label>
                    <div class="layui-input-block">
                        <input type="text" name="mount_path" lay-verify="required" lay-reqtext="名称是必填项，不能为空！"
                               placeholder="示例：pv0001" autocomplete="off" class="layui-input">
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
        layui.use(['table', 'form'], function () {
            var table = layui.table;
            var form = layui.form;
            var $ = layui.jquery;
            var csrf_token = $('[name="csrfmiddlewaretoken"]').val();

            //监听提交
            form.on('submit(btn)', function (data) {
                $.ajax({
                    url: '{% url "pv_api" %}'
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
            });
        });

    </script>
{% endblock %}
```
```python
# k8s/views.py
@k8s.self_login_required
def pv_api(request):
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    list = []
    k8s.laod_auth_config(auth_type=auth_type, token=token)
    core_api = client.CoreV1Api()
    """
    忽略不相干内容
    """

    elif request.method == "POST":
        name = request.POST.get("name")
        capacity = request.POST.get("capacity")
        access_mode = request.POST.get("access_mode", None)
        storage_type = request.POST.get("storage_type", None)
        server_ip = request.POST.get("server_ip", None)
        mount_path = request.POST.get("mount_path", None)
        # 判断命名空间是否存在
        for pv in core_api.list_persistent_volume().items:
            if name == pv.metadata.name:
                result = {'code': 1, 'msg': "持久卷已经存在！"}
                return JsonResponse(result)
        # 生成新创建资源的对象
        body = client.V1PersistentVolume(
            api_version="v1"
            , kind="PersistentVolume"
            , metadata=client.V1ObjectMeta(name=name)
            , spec=client.V1PersistentVolumeSpec(
                capacity={'storage': capacity}
                , access_modes=[access_mode]
                , nfs=client.V1NFSVolumeSource(
                    server=server_ip
                    , path="/ifs/kubernetes/%s" %mount_path
                )
            )
        )
        try:
            core_api.create_persistent_volume(body=body)
            code = 0
            msg = "success!"
        except Exception as e:
            msg = str(e)
            code = 1
        result = {'code': code, 'msg': msg}
    return JsonResponse(result)
```