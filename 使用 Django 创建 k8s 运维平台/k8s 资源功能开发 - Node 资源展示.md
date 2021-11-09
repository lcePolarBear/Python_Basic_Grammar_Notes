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
                # 判断查询指定值
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