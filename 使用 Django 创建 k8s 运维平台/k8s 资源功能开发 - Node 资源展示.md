# k8s 资源功能开发 - Node 资源展示
- 实现思路与 namespace 资源一致，都是通过前端动态数据表格展示 + 后端 api 返回数据实现资源展示
```python
# k8s/views.py
@k8s.self_login_required
def node(request):
    return render(request, "k8s/nodes.html")

@k8s.self_login_required
def node_api(request):
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    # 使用验证函数验证 token 的有效性
    k8s.laod_auth_config(auth_type=auth_type, token=token)
    core_api = client.CoreV1Api()
    list = []


    if request.method == "GET":
        try:
            # 请求存在 search_key 标识则说明为指定内容查询
            search_key = request.GET.get('search_key')
            for node in core_api.list_node_with_http_info()[0].items:
                # 获取 k8s node 属性
                name = node.metadata.name
                labels = node.metadata.labels
                status = node.status.conditions[-1].status
                scheduler = ('yes' if node.spec.unschedulable is not None else 'No')
                cpu = node.status.capacity['cpu']
                memory = node.status.capacity['memory']
                kubelet_version = node.status.node_info.kubelet_version
                cri_version = node.status.node_info.container_runtime_version
                create_time = node.metadata.creation_timestamp
                # 将 k8s node 属性添加到 list 列表
                item = {"name": name,"labels": labels, "status": status, "scheduler": scheduler, "cpu": cpu, "memory": memory, "kubelet_version": kubelet_version, "cri_version": cri_version, "create_time": create_time}
                # 判断，用以返回指定的查询值
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
        if request.GET.get('page'):
            current_page = int(request.GET.get('page', 1))
            page_item_num = int(request.GET.get('limit'))
            start = (current_page -1) * page_item_num
            end = current_page * page_item_num
            list = list[start:end]
        result = {'code': code, 'msg': msg, 'count': len(list), 'list': list}
    return JsonResponse(result)
```
```html
/* template/k8s/node.html */
{% extends 'base.html' %}
{% block title %}Nodes{% endblock %}
{% block nav-item-1 %}layui-nav-itemed{% endblock %}
{% block nav-child-1-1 %}layui-this{% endblock %}
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
                      <a class="layui-btn layui-btn-xs" lay-event="details">详情</a>
                      <a class="layui-btn layui-btn-xs layui-btn-primary" lay-event="yaml">YAML</a>
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
  var csrf_token = $('[name="csrfmiddlewaretoken"]').val();   //获取 csrf
  //动态渲染表格
  table.render({
      elem: '#test'
      ,response: {
            dataName: 'list'
      }
      ,url: '{% url 'node_api' %}' //数据接口
      ,toolbar: '#toolbarDemo' //开启头部工具栏，并为其绑定左侧模板
      //,page: true //开启分页
      ,cols: [[ //表头
          {field: 'name', title: '名称', sort: true}
          ,{field: 'labels', title: '标签', width: 320, templet: labelsFormat}
          ,{field: 'status', title: '准备就绪', width: 100}
          ,{field: 'scheduler', title: '可调度', width: 100}
          ,{field: 'cpu', title: 'CPU', width: 100}
          ,{field: 'memory', title: '内存', width: 120}
          ,{field: 'kubelet_version', title: 'kubelet 版本', width: 120}
          ,{field: 'cri_version', title: 'CRI 版本'}
          ,{field: 'create_time', title: '创建时间'}
          ,{fixed: 'right', title:'操作', toolbar: '#barDemo'}
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
                //遍历 labels 内容，并使用特殊样式渲染标出
                result += '<span style="border: 1px solid #009688;border-radius: 5px">' + key + ':' + d.labels[key] + '</span><br>'
            }
            return result
        }
    }
  //监听行工具事件
  table.on('tool(test)', function(obj){
    var data = obj.data;
    if(obj.event === 'details'){
        // 留白详情事件
    } else if(obj.event === 'yaml'){
        // 留白 YAML 事件
    }
  });
    // 监控搜索事件
    $('#searchBtn').click(function(){
        var search_key = $('input[name="name"]').val();
        //指定 id:TT 数据表格重加载
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