# 实现 namespace 资源选择功能
> 工作流程：登录成功跳转到首页 ->ajax GET 请求 namespace 接口获取所有命名空间并追究到 select 列表项，再设置 default 为默认命名空间 -> 再将当前命名空间存储到本地 session ，实现其他页面能共享获取，每次根据当前命名空间请求资源接口

### 编写 select 选择器
```html
<ul class="layui-nav layui-layout-left">
    <div class="namespace">
        <select name="namespace" id="nsselect">

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
### 将当前选择的命名空间保存到本地浏览器，使用 session 存储，以便其他页面使用
```python
# templates/base.html
<script src="/static/layui/layui.js"></script>
<script>
    layui.use(['layer'], function(){
        var $ = layui.jquery;
        var layer = layui.layer;

        $.ajax({
            type: "GET"
            ,async: false // 禁用异步以实现加载完命名空间后再执行其他操作
            ,url: "{% url 'namespace_api' %}"
            ,success: function (res) {
                if(res.code == 0){
                    for(let index in res.list){
                        row = res.list[index];
                        // 将遍历出的 namespace 值添加到 select 的 option 标签中
                        $('#nsselect').append('<option value="'+row.name+'">'+row.name+'</option>')
                    }
                    // 设置默认的命名空间
                    $('#nsselect').val('default')
                }else {
                    layer.open({
                    type: 0
                    ,title: ['命名空间查询失败！!']
                    ,content: res.msg
                })
                }
            },error: function (res) {
                layer.open({
                    type: 0
                    ,title: ['faild!']
                    ,content: res.msg
                })
            }
        })

        // 创建浏览器缓存
        var storage = window.sessionStorage;
        // 当前获取 select 标签值
        var current_ns = $("#nsselect").val()
        //查看 namespace 资源是否已选定
        var ns = storage.getItem('namespace')
        if(ns == null){
            // 没有选定则将当前 select 标签值作为选定的 namespace 值
            storage.setItem('namespace', current_ns)
        }else{
            // 若已选定则将 select 标签值改为选定的 namespace 值
            $("#nsselect").val(ns)
        }

        // 选择命名空间触发
        $("#nsselect").change(function () {
            current_ns = $("#nsselect").val();
            storage.setItem('namespace', current_ns)
        })
    });
</script>
```