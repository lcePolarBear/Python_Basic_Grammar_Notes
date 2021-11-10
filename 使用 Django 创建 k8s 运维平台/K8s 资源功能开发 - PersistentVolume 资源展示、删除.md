# K8s 资源功能开发 - PersistentVolume 资源展示、删除
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