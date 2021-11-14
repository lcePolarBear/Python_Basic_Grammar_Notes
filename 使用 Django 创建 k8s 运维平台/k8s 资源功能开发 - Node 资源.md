# k8s 资源功能开发 - Node 资源
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
<!-- template/k8s/node.html -->
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
### 实现 Node 资源的详情展示
- 展示节点的资源，展示节点的信息，展示节点的容器信息
```html
<!--template/k8s/node_details.html-->
{% extends "base.html" %}
{% block title %}Nodes{% endblock %}
{% block nav-item-1 %}layui-nav-itemed{% endblock %}
{% block nav-child-1-1 %}layui-this{% endblock %}

{% block content %}
    <div class="layui-col-md12 layui-col-space10">
        <div class="layui-col-md6">
            <div class="layui-card">
                <div class="layui-card-header">节点资源</div>
                <div class="layui-card-body">
                    CPU：
                    <span class="layui-badge layui-bg-orange"> 已分配 {{ node_resouces.cpu_requests }} 核 / 可分配 {{ node_resouces.allocatable_cpu }} 核 / 总量 {{ node_resouces.capacity_cpu }} 核</span>
                    <hr class="layui-bg-gray">
                    内存：
                    <span class="layui-badge layui-bg-orange"> 已分配 {{ node_resouces.memory_requests }} G / 可分配 {{ node_resouces.allocatable_memory }} G / 总量 {{ node_resouces.capacity_memory }} G</span>
                    <hr>
                    短暂存储：
                    <span class="layui-badge layui-bg-green">可分配 {{ node_resouces.allocatable_ephemeral_storage }} G / 总量 {{ node_resouces.capacity_ephemeral_storage }} G</span>
                    <hr class="layui-bg-gray">
                    Pod数量：
                    <span class="layui-badge layui-bg-green">已创建 {{ node_resouces.pods_number }} 个 / 总量 {{ node_resouces.capacity_pods }} 个</span>
                    <hr class="layui-bg-gray">
                </div>
            </div>
        </div>
        <div class="layui-col-md6">
            <div class="layui-card">
                <div class="layui-card-header">节点信息</div>
                <div class="layui-card-body">
                    节点名称：{{ node_info.node_name }}
                    <hr class="layui-bg-gray">
                    主机名：{{ node_info.hostname }}
                    <hr class="layui-bg-gray">
                    内部IP：{{ node_info.internal_ip }}
                    <hr class="layui-bg-gray">
                    Pod网络：{{ node_info.pod_cidr }}
                    <hr class="layui-bg-gray">
                    操作系统：{{ node_info.os }}
                    <hr class="layui-bg-gray">
                    内核：{{ node_info.kernel }}
                    <hr class="layui-bg-gray">
                    CPU架构：{{ node_info.cpu_arch }}
                    <hr class="layui-bg-gray">
                    容器引擎：{{ node_info.container_runtime_version }}
                    <hr class="layui-bg-gray">
                    kubelet版本：{{ node_info.kubelet_version }}
                    <hr class="layui-bg-gray">
                    kube-proxy版本：{{ node_info.kube_proxy_version }}
                    <hr class="layui-bg-gray">
                    不可调度：{{ node_info.unschedulable }}
                    <hr class="layui-bg-gray">
                    标签：
                    {% for k,v in node_info.labels.items %}
                        <span style='border: 1px solid #d6e5ec;border-radius: 20px;padding: 1px 6px 1px 6px'>{{ k }}:{{ v }}</span>
                    {% endfor %}
                    <hr class="layui-bg-gray">
                    污点：
                    {% if node_info.taints %}
                        {% for i in node_info.taints %}
                            <span style='border: 1px solid #d6e5ec;border-radius: 20px;padding: 1px 6px 1px 6px'>{{ i.key }}={{ i.value }}[{{ i.effect }}]</span>
                        {% endfor %}
                    {% else %}
                        None
                    {% endif %}
                    <hr class="layui-bg-gray">
                </div>
            </div>
        </div>
        <div class="layui-col-md12">
            <div class="layui-card">
                <div class="layui-card-header">容器信息</div>
                <div class="layui-card-body">
                    <table class="layui-hide" id="test" lay-filter="test"></table>
                </div>
            </div>
        </div>
    </div>

{% endblock %}

{% block ex_js %}
    <script>

        layui.use('table', function () {
            var table = layui.table;
            table.render({
                elem: '#test'
                , response: {
                    dataName: "list"
                }
                , url: '{% url 'node_details_pod_list' %}?node_name=' + '{{ node_name }}'
                , cols: [[
                    {field: 'pod_name', title: 'Pod名称', sort: true}
                    , {field: 'namespace', title: '命名空间', sort: true}
                    , {field: 'status', title: '运行状态', sort: true}
                    , {field: 'pod_ip', title: 'Pod IP'}
                    , {field: 'cpu_requests', title: 'CPU请求', sort: true}
                    , {field: 'cpu_limits', title: 'CPU限制', sort: true}
                    , {field: 'memory_requests', title: '内存请求', sort: true}
                    , {field: 'memory_limits', title: '内存限制', sort: true}
                    , {field: 'create_time', title: '创建时间'}
                ]]
                , page: true
            });

        });

    </script>
{% endblock %}
```
```html
<!--template/k8s/nodes.html-->
<script>
//监听行工具事件
        table.on('tool(test)', function (obj) {
            var data = obj.data;
            //console.log(obj)
            if (obj.event === 'details') {
                window.location.href = "{%  url 'node_details' %}?node_name=" + data.name
            } else if (obj.event === 'edit') {
                // 查看YAML
            }
        });
</script>
```
```python
# dashboard/node_details.py
# 用于提供节点资源和信息的数据
from kubernetes import client, config
from devops import k8s  # 使用时间格式化
import re

# Node详情和仪表盘使用

# CPU单位转浮点数
def cpuUnitToF(str):
    if str.endswith("m"):
        n = re.findall("\d+",str)[0]
        n = round(float(n) / 1000,2)
        return n
    else:
        return float(str)

# 内存单位转GB
def memoryUnitToG(str):
    if str.endswith("M") or  str.endswith("Mi"):
        m = re.findall("\d+", str)[0]
        g = round(float(m) / 1024,2)
        return g
    elif str.endswith("K") or str.endswith("Ki"):
        k = re.findall("\d+", str)[0]
        g = round(float(k) / 1024 / 1024, 2)
        return  g
    elif str.endswith("G") or str.endswith("Gi"):
        g = re.findall("\d+", str)[0]
        return float(g)

def node_info(core_api, n_name=None):
    node_info = {}
    for node in core_api.list_node().items:
        node_name = node.metadata.name
        node_info[node_name] = {"node_name":"","hostname": "", "internal_ip": "","os": "", "cpu_arch":"", "kernel": "","pod_cidr":"",
                                "container_runtime_version":"","kubelet_version": "","kube_proxy_version":"", "labels": "","unschedulable":"","taints": "", "create_time": ""}
        node_info[node_name]["node_name"] = node_name
        for i in node.status.addresses:
            if i.type == "InternalIP":
                node_info[node_name]["internal_ip"] = i.address
            elif i.type == "Hostname":
                node_info[node_name]["hostname"] = i.address
        node_info[node_name]["pod_cidr"] = node.spec.pod_cidr
        node_info[node_name]["os"] = node.status.node_info.os_image
        node_info[node_name]["kernel"] = node.status.node_info.kernel_version
        node_info[node_name]["cpu_arch"] = node.status.node_info.architecture
        node_info[node_name]["container_runtime_version"] = node.status.node_info.container_runtime_version
        node_info[node_name]["kubelet_version"] = node.status.node_info.kubelet_version
        node_info[node_name]["kube_proxy_version"] = node.status.node_info.kube_proxy_version
        node_info[node_name]["unschedulable"] = ("是" if node.spec.unschedulable else "否")
        node_info[node_name]["labels"] = node.metadata.labels
        node_info[node_name]["taints"] = node.spec.taints
        node_info[node_name]["create_time"] = k8s.dt_format(node.metadata.creation_timestamp)

    if n_name is None:
        return node_info
    else:
        return node_info[n_name]

def node_resource(core_api, n_name=None):
    """
    统计node上所有容器资源分配
    最终生成字典格式：
    {"k8s-node1": {"allocatable_cpu": "","allocatable_memory":"","cpu_requests":"", "cpu_limits":"", "memory_requests": "", "memory_limits":""},"k8s-node2": {"cpu_requests":"", "cpu_limits":"", "memory_requests": "", "memory_limits":""}}
    """
    node_resource  = {}
    for node in core_api.list_node().items:
        node_name = node.metadata.name
        node_resource[node_name] = {"allocatable_cpu": "", "capacity_cpu":"", "allocatable_memory": "","capacity_memory":"",
                            "allocatable_ephemeral_storage": "","capacity_ephemeral_storage":"","capacity_pods":"", "pods_number": 0,
                            "cpu_requests": 0, "cpu_limits": 0,"memory_requests": 0, "memory_limits": 0}
        # 可分配资源
        allocatable_cpu = node.status.allocatable['cpu']
        allocatable_memory = node.status.allocatable['memory']
        print(allocatable_memory)
        allocatable_storage = node.status.allocatable['ephemeral-storage']
        node_resource[node_name]["allocatable_cpu"] = int(allocatable_cpu)
        node_resource[node_name]["allocatable_memory"] = memoryUnitToG(allocatable_memory)
        node_resource[node_name]["allocatable_ephemeral_storage"] = round(int(allocatable_storage) / 1024 / 1024 / 1024,2)

        # 总容量
        capacity_cpu = node.status.capacity['cpu']
        capacity_memory = node.status.capacity['memory']
        print(capacity_memory)
        capacity_storage = node.status.capacity['ephemeral-storage']
        capacity_pods = node.status.capacity['pods']
        node_resource[node_name]["capacity_cpu"] = int(capacity_cpu)
        node_resource[node_name]["capacity_memory"] = memoryUnitToG(capacity_memory)
        node_resource[node_name]["capacity_ephemeral_storage"] = memoryUnitToG(capacity_storage)
        node_resource[node_name]["capacity_pods"] = capacity_pods

        # 调度 & 准备就绪
        schedulable = node.spec.unschedulable
        status = node.status.conditions[-1].status  # 取最新状态
        node_resource[node_name]["schedulable"] = schedulable
        node_resource[node_name]["status"] = status

    # 如果不传节点名称计算资源请求和资源限制并汇总，否则返回节点资源信息
    for pod in core_api.list_pod_for_all_namespaces().items:
      pod_name = pod.metadata.name
      node_name = pod.spec.node_name
      # 如果节点名为None，说明该Pod未成功调度创建，跳出循环，不计算其中
      if node_name is None:
          continue

      # 遍历pod中容器
      for c in pod.spec.containers:
          c_name = c.name
          # 资源请求
          if c.resources.requests is not None:
              if "cpu" in c.resources.requests :
                  cpu_request = c.resources.requests["cpu"]
                  # 之前用 += 方式，但浮点数运算时会出现很多位小数，所以要用round取小数
                  node_resource[node_name]['cpu_requests'] = round(node_resource[node_name]['cpu_requests'] + cpuUnitToF(cpu_request),2)
              if  "memory" in c.resources.requests:
                  memory_request = c.resources.requests["memory"]
                  node_resource[node_name]['memory_requests'] = round(node_resource[node_name]['memory_requests'] + memoryUnitToG(memory_request),2)
          # 资源限制
          if c.resources.limits is not None:
              if  "cpu" in c.resources.limits :
                  cpu_limit = c.resources.limits["cpu"]
                  node_resource[node_name]['cpu_limits'] = round(node_resource[node_name]['cpu_limits'] + cpuUnitToF(cpu_limit),2)
              if "memory" in c.resources.limits:
                  memory_limit = c.resources.limits["memory"]
                  node_resource[node_name]['memory_limits'] = round(node_resource[node_name]['memory_limits'] + memoryUnitToG(memory_limit),2)
      # 添加Pod数量
      node_resource[node_name]['pods_number'] += 1
    if n_name is None:
        return node_resource
    else:
        return node_resource[n_name]

if __name__ == "__main__":
    config.load_kube_config("upload/k8s.kubeconfig")
    core_api = client.CoreV1Api()  # namespace,pod,service
    # print(node_pods(core_api,"k8s-node1"))
    # print(node_resource(core_api))
    # print(node_info(core_api))

```
```python
# k8s/views.py
# 用于返回节点资源和信息数据
@k8s.self_login_required
def node_details(request):
    from dashboard import node_data
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    list = []
    k8s.laod_auth_config(auth_type=auth_type, token=token)
    core_api = client.CoreV1Api()
    node_name = request.GET.get('node_name')
    # 从 node_details 脚本获取信息
    node_resource = node_data.node_resource(core_api=core_api, n_name=node_name)
    node_info = node_data.node_info(core_api=core_api, n_name=node_name)
    print(node_resource)
    print(node_info)
    return render(request, "k8s/node_details.html",
                  {"node_name": node_name, "node_resouces": node_resource, "node_info": node_info})


# 用于返回 node 资源的 pod 信息
@k8s.self_login_required
def node_details_pod_list(request):
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    k8s.laod_auth_config(auth_type=auth_type,token=token)
    core_api = client.CoreV1Api()

    node_name = request.GET.get("node_name", None)

    list = []
    try:
        for pod in core_api.list_pod_for_all_namespaces().items:
            name = pod.spec.node_name
            pod_name = pod.metadata.name
            namespace = pod.metadata.namespace
            status = ("运行中" if pod.status.conditions[-1].status else "异常")
            host_network = pod.spec.host_network
            pod_ip = ("主机网络" if host_network else pod.status.pod_ip)
            create_time = k8s.dt_format(pod.metadata.creation_timestamp)

            if name == node_name:
                if len(pod.spec.containers) == 1:
                    cpu_requests = "0"
                    cpu_limits = "0"
                    memory_requests = "0"
                    memory_limits = "0"
                    for c in pod.spec.containers:
                        # c_name = c.name
                        # c_image= c.image
                        cpu_requests = "0"
                        cpu_limits = "0"
                        memory_requests = "0"
                        memory_limits = "0"
                        if c.resources.requests is not None:
                            if "cpu" in c.resources.requests:
                                cpu_requests = c.resources.requests["cpu"]
                            if "memory" in c.resources.requests:
                                memory_requests = c.resources.requests["memory"]
                        if c.resources.limits is not None:
                            if "cpu" in c.resources.limits:
                                cpu_limits = c.resources.limits["cpu"]
                            if "memory" in c.resources.limits:
                                memory_limits = c.resources.limits["memory"]
                else:
                    c_r = "0"
                    c_l = "0"
                    m_r = "0"
                    m_l = "0"
                    cpu_requests = ""
                    cpu_limits = ""
                    memory_requests = ""
                    memory_limits = ""
                    for c in pod.spec.containers:
                        c_name = c.name
                        # c_image= c.image
                        if c.resources.requests is not None:
                            if "cpu" in c.resources.requests:
                                c_r = c.resources.requests["cpu"]
                            if "memory" in c.resources.requests:
                                m_r = c.resources.requests["memory"]
                        if c.resources.limits is not None:
                            if "cpu" in c.resources.limits:
                                c_l = c.resources.limits["cpu"]
                            if "memory" in c.resources.limits:
                                m_l = c.resources.limits["memory"]

                        cpu_requests += "%s=%s<br>" % (c_name, c_r)
                        cpu_limits += "%s=%s<br>" % (c_name, c_l)
                        memory_requests += "%s=%s<br>" % (c_name, m_r)
                        memory_limits += "%s=%s<br>" % (c_name, m_l)

                pod = {"pod_name": pod_name, "namespace": namespace, "status": status, "pod_ip": pod_ip,
                       "cpu_requests": cpu_requests, "cpu_limits": cpu_limits, "memory_requests": memory_requests,
                       "memory_limits": memory_limits, "create_time": create_time}
                list.append(pod)

        current_page = int(request.GET.get('page', 1))
        page_item_num = int(request.GET.get('limit', 10))
        page_item_num = int(request.GET.get('limit', 10))
        start = (current_page - 1) * page_item_num
        end = current_page * page_item_num
        list = list[start:end]

        code = 0
        msg = "获取数据成功"
        res = {"code": code, "msg": msg, "count": len(list), "list": list}
        return JsonResponse(res)
    except Exception as e:
        status = getattr(e, "status")
        if status == 403:
            msg = "没有访问权限！"
        else:
            msg = "查询失败！"
        res = {"code": 1, "msg": msg}
        return JsonResponse(res)
```