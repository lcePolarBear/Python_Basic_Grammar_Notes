# Layui 的动态数据表格
## 创建 layui 动态数据表格模板
1. 官方动态数据表格文档
2. 导入并修改动态数据表格模板代码
    ```html
    {% extends 'base.html' %}
    {% block title %}首页{% endblock %}
    {% block content %}

        <script src="/static/layui/layui.js"></script>
        <table id="demo" lay-filter="test"></table>
        <script>
        layui.use(['table'], function () {
            var table = layui.table;

            table.render({
            elem: '#demo' //指定原始表格元素选择器（推荐id选择器）
            ,height: 315 //容器高度
                ,url: '/user'
            ,cols: [[
                {checkbox: true}
                ,{field: 'id', title: 'ID', width: 80, sort: true}
                ,{field: 'username', title: '用户名', width: 120}
                ,{field: 'age', title: '年龄', width: 120}
                ]] //设置表头
            //,…… //更多参数参考右侧目录：基本参数选项
            });
        })
        </script>

    {% endblock %}
    ```
3. 创建后端响应
    ```py
    def user(request):
        """
        数据表格接受的数据格式：
        {
        "code": 0,
        "totalRow": {
            "score": "666"
            ,"experience": "999"
        },
        "data": [{}, {}],
        "msg": "",
        "count": 1000
        }
        :param request:
        :return:
        """
        # 模拟从数据库拉取数据
        try:
            code = 0
            data = [{'id': 1,'username': 'chen', 'age': 25},{'id': 2,'username': 'kun', 'age': 15}]
            msg = "获取数据成功"
        except Exception:
            data = None
            code = 1
            msg = "获取数据失败"

        result = {'code':code, 'msg': msg, 'data': data, 'count': ''}
        return JsonResponse(result)
    ```
4. 添加表格样式
    ```html
    <!--index.html-->
    {% extends 'base.html' %}
    {% block title %}首页{% endblock %}
    {% block content %}

        <script src="/static/layui/layui.js"></script>
        <table id="demo" lay-filter="test"></table>
        <script>
        layui.use(['table'], function () {
            var table = layui.table;

            table.render({
                elem: '#demo' //指定原始表格元素选择器（推荐id选择器）
                ,height: 315 //容器高度
                ,toolbar: '#toolbarDemo'    //开启表格头部工具栏区域
                ,defaultToolbar: ['filter', 'print', 'exports', {   //头部工具栏右侧图标
                    title: '提示' //标题
                    ,layEvent: 'LAYTABLE_TIPS' //事件名，用于 toolbar 事件中使用
                    ,icon: 'layui-icon-tips' //图标类名
                }]
                ,url: '/user'
                ,cols: [[
                {checkbox: true}
                ,{field: 'id', title: 'ID', width: 80, sort: true}
                ,{field: 'username', title: '用户名', width: 120}
                ,{field: 'age', title: '年龄', width: 120}
                ]] //设置表头
                ,page: true //设置分页
            });
        })
        </script>

    {% endblock %}
    ```
    ```python
    # views.py
    def user(request):
        page = int(request.GET.get('page'))
        limit = int(request.GET.get('limit'))

        # 拿到切片的起始值和终止值
        start = (page -1) * limit
        end = page * limit
        """
        访问数据表格，每个页面显示十条数据
        默认会自动传递两个参数：?page=1&limit=30（该参数可通过 request 自定义），page 代表当前页码、limit 代表每页数据量
        """

        """
        数据表格接受的数据格式：
        {
        "code": 0,
        "totalRow": {
            "score": "666"
            ,"experience": "999"
        },
        "data": [{}, {}],
        "msg": "",
        "count": 1000
        }
        :param request:
        :return:
        """
        try:
            code = 0
            # 在此处可以连接数据库获取数据，并返回给表格
            data = [{'id': 1,'username': 'chen', 'age': 25},{'id': 2,'username': 'kun', 'age': 15}]
            msg = "获取数据成功"
        except Exception:
            data = None
            code = 1
            msg = "获取数据失败"

        //获取所有数据的总数
        count = len(data)

        //使用切片获取到的所需分页 的起始数据和最后数据
        data = data[start:end]

        result = {'code':code, 'msg': msg, 'data': data, 'count': count}
        return JsonResponse(result)
    ```
5. 添加头部工具栏和行工具条
    ```html
    <!--index.html-->
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Title</title>
        <link rel="stylesheet" href="/static/layui/css/layui.css">
        <script src="/static/layui/layui.js"></script>
    </head>
    <body>

    <!--创建动态表格 table-->
    <table id="demo" lay-filter="test">
        {% csrf_token %}
    </table>
    <!--添加头部工具栏-->
    <script type="text/html" id="toolbarDemo">
    <div class="layui-btn-container">
        <button class="layui-btn layui-btn-sm" lay-event="getCheckData">获取选中行数据</button>
        <button class="layui-btn layui-btn-sm" lay-event="getCheckLength">获取选中数目</button>
        <button class="layui-btn layui-btn-sm" lay-event="isAll">验证是否全选</button>
    </div>
    </script>
    <!--添加工具条-->
    <script type="text/html" id="barDemo">
    <a class="layui-btn layui-btn-xs" lay-event="edit">编辑</a>
    <a class="layui-btn layui-btn-danger layui-btn-xs" lay-event="del">删除</a>
    </script>

    <script>
    layui.use(['table'], function () {
        var table = layui.table;
        //表格样式设置
        table.render({
            // 此处省略...
        });

        //头工具栏事件
        table.on('toolbar(test)', function (obj) {
            var checkStatus = table.checkStatus(obj.config.id);
            switch (obj.event) {
                case 'getCheckData':
                    var data = checkStatus.data;
                    layer.alert(JSON.stringify(data));
                    break;
                case 'getCheckLength':
                    var data = checkStatus.data;
                    layer.msg('选中了：' + data.length + ' 个');
                    break;
                case 'isAll':
                    layer.msg(checkStatus.isAll ? '全选' : '未全选');
                    break;

                //自定义头工具栏右侧图标 - 提示
                case 'LAYTABLE_TIPS':
                    layer.alert('这是工具栏右侧自定义的一个图标按钮');
                    break;
            }
            ;
        });
        //监听行工具栏
        table.on('tool(test)', function (obj) {
            var $ = layui.jquery;
            var data = obj.data;    //获取表中操作的行对象
            var csrf_token = $('[name="csrfmiddlewaretoken"]').val();   //获取 csrf
            if(obj.event == 'del'){ //相应删除事件
                layer.confirm('真的删除行么', function (index) {
                    var info = {'id': data.id};
                    $.ajax({
                        type: "DELETE"
                        ,url: "/user"
                        ,data: info
                        ,headers: {'X-CSRFToken': csrf_token}   //使用表头传输 csrf 避免传输失败
                        ,success: function (result) {
                            if(result.code == '0'){
                                obj.del();
                                layer.close(index);
                                layer.msg(result.msg)
                            }else{
                                layer.msg(result.msg)
                            }
                        }
                        ,error: function () {
                            layer.msg("服务器接口异常")
                        }
                    })
                });
            }else if(obj.event == 'edit'){  //相应编辑事件
                layer.prompt({
                    formType: 2
                    ,value: data.username
                }, function (value, index) {
                    var info = {'id': data.id, 'username': value};
                    $.ajax({
                        type: "PUT"
                        ,url: "/user"
                        ,data: info
                        ,headers: {'X-CSRFToken': csrf_token}
                        ,success: function (result) {
                            if(result.code == '0'){
                                obj.update({
                                    username: value
                                });
                                layer.close(index)
                                layer.msg(result.msg)
                            }else{
                                layer.msg(result.msg)
                            }
                        }
                        ,error: function () {
                            layer.msg("服务器接口异常")
                        }
                    });
                });
            }
        });
    });
    </script>
    </body>
    </html>
    ```
    ```python
    # views.py
    def user(request):
        if request.method == "GET":
            """
            此处省略
            """
            return JsonResponse(result)
        elif request.method == "POST":
            pass
        elif request.method == "DELETE":    # 响应监听行工具栏的删除事件
            # 数据库操作过程
            code = 0
            msg = "删除数据成功"
            result = {'code': code, 'msg': msg}
            return JsonResponse(result)
        elif request.method == "PUT":       # # 响应监听行工具栏的编辑事件
            # 数据库操作过程
            code = 0
            msg = "修改数据成功"
            result = {'code': code, 'msg': msg}
            return JsonResponse(result)
        else:
            return "操作方法不允许!"
    ```