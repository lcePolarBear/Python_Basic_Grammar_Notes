# Layui 的使用方法和基础组件
## Layui 与 Django 的集成方式
1. 获取 Layui 框架包 [官方地址](https://www.layui.com/)
2. Django 根目录创建 static 文件夹并将 layui 目录放入其中
    ```
    ├─css //css目录
    │  │─modules //模块 css 目录（一般如果模块相对较大，我们会单独提取，如下：）
    │  │  ├─laydate
    │  │  └─layer
    │  └─layui.css //核心样式文件
    ├─font  //字体图标目录
    └─layui.js //核心库
    ```
3. settings.py 文件创建静态数据元组，将 static 路径导入到项目
    ```py
    STATICFILES_DIRS = (
        os.path.join(BASE_DIR, 'static'),
    )
    ```
4. html 导入 layui.css 和 layui.js
    ```html
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Title</title>
        <link rel="stylesheet" href="/static/layui/css/layui.css">
        <script src="/static/layui/layui.js"></script>
    </head>
    <body>
    
    </body>
    </html>
    ```
5. 测试 Hello World
    ```html
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Title</title>
        <link rel="stylesheet" href="/static/layui/css/layui.css">
        <script src="/static/layui/layui.js"></script>
    </head>
    <body>
    <script>
    layui.use(['layer', 'form'], function(){
    var layer = layui.layer
    ,form = layui.form;

    layer.msg('Hello World');
    });
    </script>
    </body>
    </html>
    ```

## 改造 layui 后台管理界面布局 html 代码，创建 DevOps 管理后台界面
1. [Layui 布局文档](https://www.layui.com/doc/element/layout.html)
2. 使用 {% extends 'base.html' %} 创建页面布局的模板，用于其他子页面调用布局菜单
3. 使用 `<dd class="{% block nav-child-1-2 %}{% endblock %}">` 将 layui 样式由子页面调入模板页面
    ```html
    <!--pods.html-->
    {% extends "base.html" %}
    {% block title %}Pods{% endblock %}
    {% block nav-child-1-1%}layui-this{% endblock %}
    {% block content %}
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Title</title>
    </head>
    <body>
    <h1>pod 列表</h1>
    </body>
    </html>
    {% endblock %}
    ```
    ```html
    <!--base.html 引用的 Layui 官方布局代码-->
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
    <title>{% block title %}{% endblock %}</title>
    <link rel="stylesheet" href="/static/layui/css/layui.css">
    </head>
    <body>
    <div class="layui-layout layui-layout-admin">
    <div class="layui-header layui-bg-black">
        <!--顶部背景 div （忽略代码）-->
    </div>

    <div class="layui-side layui-bg-cyan">
        <div class="layui-side-scroll">
        <!-- 左侧导航区域（可配合layui已有的垂直导航） -->
        <ul class="layui-nav layui-nav-tree layui-bg-cyan" lay-filter="test">
            <li class="layui-nav-item layui-nav-itemed">
            <a class="" href="javascript:;">工作负载</a>
            <dl class="layui-nav-child">
                <!--添加 block 用于从子页面传入 layui-this 选项触发选中样式-->
                <dd class="{% block nav-child-1-1 %}{% endblock %}"><a href="{% url "pods" %}">Pods</a></dd>
                <dd class="{% block nav-child-1-2 %}{% endblock %}"><a href="{% url "deployments" %}">Deplyments</a></dd>
            </dl>
            </li>
            <li class="layui-nav-item layui-nav-itemed">
            <a href="javascript:;">负载均衡</a>
            <dl class="layui-nav-child">
                <dd class="{% block nav-child-2-1 %}{% endblock %}"><a href="{% url "services" %}">Services</a></dd>
                <dd class="{% block nav-child-2-2 %}{% endblock %}"><a href="{% url "ingress" %}">Ingress</a></dd>
            </dl>
            </li>
        </ul>
        </div>
    </div>

    <div class="layui-body">
        <!-- 内容主体区域 -->
        <div style="padding: 15px;">{% block content %}{% endblock %}</div>
    </div>

    <div class="layui-footer">
        <!-- 底部固定区域 -->
        底部固定区域
    </div>
    </div>
    <script src="/static/layui/layui.js"></script>
    <script>
    //JS
    layui.use(['element', 'layer', 'util'], function(){
    var element = layui.element
    ,layer = layui.layer
    ,util = layui.util
    ,$ = layui.$;

    //头部事件
    util.event('lay-header-event', {
        //左侧菜单事件
        menuLeft: function(othis){
        layer.msg('展开左侧菜单的操作', {icon: 0});
        }
        ,menuRight: function(){
        layer.open({
            type: 1
            ,content: '<div style="padding: 15px;">处理右侧面板的操作</div>'
            ,area: ['260px', '100%']
            ,offset: 'rt' //右上角
            ,anim: 5
            ,shadeClose: true
        });
        }
    });

    });
    </script>
    </body>
    </html>
    ```

## 美化管理界面细节部分
1. 导航栏添加 icon 字体和图标
    ```html
    <li class="layui-nav-item"><a href="javascript:;"><i class="layui-icon layui-icon-home">&nbsp;&nbsp;平台概述</i></a></li>
    ```
2. 栅格系统的应用
    - layui 将页面按列分为 12 等份， `layui-col-md*` 控制当前标签所占的 * 份
    ```html
    {% extends 'base.html' %}
    {% block title %}首页{% endblock %}
    {% block content %}

    <div class="layui-row layui-col-space10">
        <!--div 占列的 9/12 -->
        <div class="layui-col-md9">
            <!--开启行管控，实现栅格嵌套，子标签得以并列显示-->
            <div class="layui-row">
                <div class="layui-col-md6" style="background-color: blue">2/3</div>
                <div class="layui-col-md6" style="background-color: rebeccapurple">2/3</div>
            </div>
        </div>
        <!--div 占列的 3/12 份-->
        <div class="layui-col-md3">
            <div style="background-color: red">1/3</div>
        </div>
    </div>

    {% endblock %}
    ```
3. 卡片的应用
    ```html
    <div class="layui-card">
    <div class="layui-card-header">
        卡片面板
    </div>
    <div class="layui-card-body">
        卡片式面板面板通常用于非白色背景色的主体内<br>
        从而映衬出边框投影
    </div>
    </div>
    ```
4. 按钮的应用
    ```html
    <button type="button" class="layui-btn">一个标准的按钮</button>
    <a href="http://www.layui.com" class="layui-btn">一个可跳转的按钮</a>
    ```
    - 官方提供了丰富的按钮样式 class [Layui 按钮示例](https://www.layui.com/demo/button.html)