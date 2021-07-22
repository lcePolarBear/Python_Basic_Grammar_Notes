# jQuery 操作 HTML

## 案例：显示和隐藏元素
```js
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <script src="/Web/static/js/jquery.min.js"></script>
</head>
<body>
<button id="hide" type="button">隐藏</button>
<button id="show" type="button">显示</button>
<button id="toggle" type="button">切换</button>
<p id="demo">this is a txt</p>
<script type="text/javascript">
    $("#hide").click(function () {
        $("#demo").hide();
    });
    $("#show").click(function () {
        $("#demo").show();
    });
    $("#toggle").click(function () {
        $("#demo").toggle();
    });
</script>
</body>
</html>
```

## 获取与设置内容
```js
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <script src="/Web/static/js/jquery.min.js"></script>
</head>
<body>
<input type="text" id="name" name="name">
<p id="txt">是一个<b>大好人</b>。</p>
<button id="btn1" type="button">显示文本</button>
<button id="btn2" type="button">显示 HTML</button>
<button id="btn3" type="button">显示文本框</button>
<p id="demo"></p>
<script type="text/javascript">
    $("#btn1").click(function () {
        x = $("#txt").text();
        $("#demo").text(x).css("color","red");  //不会解析b标签
    });
    $("#btn2").click(function () {
        x = $("#txt").html();
        $("#demo").html(x).css("color","red")   //会解析b标签
    });
    $("#btn3").click(function () {
        x = $("#name").val();                   
        $("#demo").text(x+).css("color","red")   //解析文本框内容
    });
</script>
</body>
</html>
```

## 获取、设置和删除属性
