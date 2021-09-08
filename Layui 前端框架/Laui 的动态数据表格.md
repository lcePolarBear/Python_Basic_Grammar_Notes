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
            data = [{'id': 1,'username': 'chen', 'age': 25},{'id': 2,'username': 'kun', 'age': 15}]
            msg = "获取数据成功"
        except Exception:
            data = None
            code = 1
            msg = "获取数据失败"

        count = len(data)

        data = data[start:end]

        result = {'code':code, 'msg': msg, 'data': data, 'count': count}
        return JsonResponse(result)
    ```