# 实现 namespace 资源选择功能
> 工作流程：登录成功跳转到首页 ->ajax GET 请求 namespace 接口获取所有命名空间并追究到 select 列表项，再设置 default 为默认命名空间 -> 再将当前命名空间存储到本地 session ，实现其他页面能共享获取，每次根据当前命名空间请求资源接口

### 编写 select 选择器
```html
<ul class="layui-nav layui-layout-left">
    <div class="namespace">
        <select name="namespace" id="nsselect">
            <option value="test1">test1</option>
            <option value="test2">test2</option>
        </select>
    </div>
</ul>
```
使用 jquery 从后台获取 namespace 资源的数据
```js
<script>
    layui.use(['layer'], function(){
        var $ = layui.jquery;
        var layer = layui.layer;

        $.ajax({
            type: "GET"
            ,url: "{% url 'namespace_api' %}"
            ,success: function (res) {
                if(res.code == 0){
                    for(let index in res.list){
                        row = res.list[index];
                        $('#nsselect').append('<option value="'+ row.name +'">'+row.name+'</option>')
                    }
                }else {

                }
            },error: function (res) {
                layer.open({
                    type: 0
                    ,title: ['faild!']
                    ,content: res.msg
                })
            }
        })
    })
</script>
```
- 抽象 k8s 验证功能
```python
# devops/k8s.py
# 加载认证配置
def laod_auth_config(auth_type, token):
    if auth_type == "token":
        # 验证 token 是否有效，有效则跳转到首页
        configuration = client.Configuration()
        configuration.host = api_server
        configuration.verify_ssl = False
        configuration.api_key = {"authorization": "Bearer " + token}
        client.Configuration.set_default(configuration)
    elif auth_type == "kubeconfig":
        user = User.objects.filter(token = token)
        content = user[0].content
        yaml_content = yaml.load(content, Loader=yaml.FullLoader)
        config.load_kube_config_from_dict(yaml_content)
```
```python
# k8s/views.py
@k8s.self_login_required
def namespace_api(request):
    if request.method == "GET":
        # 调用 k8s api 从而获得命名空间
        auth_type = request.session.get("auth_type")
        token = request.session.get("token")
        list = []
        k8s.laod_auth_config(auth_type=auth_type, token=token)
        apps_api = client.CoreV1Api()
        try:
            for ns in apps_api.list_namespace().items:
                name = ns.metadata.name
                labels = ns.metadata.labels
                create_time = ns.metadata.creation_timestamp
                item = {'name': name, 'labels': labels, 'create_time': create_time}
                list.append(item)
            code = 0
            msg = "success!"
        except Exception as e:
            status = getattr(e, 'status')
            code = status
            msg = "faild!"

        result = {'code': code, 'msg': msg, 'count': len(list), 'list': list}
        return JsonResponse(result)
```