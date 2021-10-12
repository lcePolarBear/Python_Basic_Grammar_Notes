# layui 的弹出层
> [官网网站链接](https://www.layui.com/doc/modules/layer.html)

## 创建弹出层
```html
<script>
    layui.use(['layer'], function(){
        // Layui 的模块
        var layer = layui.layer;
        var $ = layui.jquery;
        $('#btn').click(function () {
            layer.open({
                type: 2,  // 层类型
                title: ['弹窗名称', 'font-size:18px;'],
                area: ['60%', '40%'], // 或者是像素
                content: 'http://www.baidu.com'
                });
        })
    });
</script>
```
### layer提供了5种层类型。可传入的值有：
- 0（信息框，默认）：输出一个文本
- 1（页面层）：输出一段 HTML 内容
- 2（iframe层）：加载网址