# jQuery 操作 HTML

## 显示和隐藏元素
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

## 获取与设置元素内容
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

## 获取、设置和删除元素属性
```js
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <script src="/Web/static/js/jquery.min.js"></script>
</head>
<body>
<a href="http://www.baidu.com" id="a1">www.baidu.com</a></br>
<button id="btn1" type="button">查看元素指定的属性值</button>
<button id="btn2" type="button">设置元素指定的属性值</button>
<button id="btn3" type="button">删除元素指定的属性值</button>
<p id="demo"></p>
<script type="text/javascript">
    $("#btn1").click(function () {
        x = $("#a1").attr("href");  //获取元素的属性
        $("#demo").text(x)  //
    });
    $("#btn2").click(function () {
        x = $("#a1").attr("href","http://map.baidu.com");   //修改元素的属性
    });
    $("#btn3").click(function () {
        x = $("#a1").removeAttr("href");    //删除掉元素的属性
    });
</script>
</body>
</html>
```

## 添加元素
```js
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <script src="/Web/static/js/jquery.min.js"></script>
</head>
<body>
<div id="v0">v0
    <div id="v1">v1
        <div id="v2">v2</div>
        <div id="v3">v3</div>
    </div>
    v0-end
</div>
<button id="btn1">在被选中元素的结尾插入</button>
<button id="btn2">在被选中元素的开头插入</button>
<button id="btn3">在被选中元素之后插入</button>
<button id="btn4">在被选中元素之前插入</button>
<script type="text/javascript">
    $("#btn1").click(function () {
        $("#v1").append("btn1"); //在被选中元素的结尾插入内容或者元素
    })
</script>
<script type="text/javascript">
    $("#btn2").click(function () {
        $("#v1").prepend("<p>btn2</p>");   //在被选中元素的开头插入内容或者元素
    })
</script>
<script type="text/javascript">
    $("#btn3").click(function () {
        $("#v1").after("btn3"); //在被选中元素之后插入内容或者元素
    })
</script>
<script type="text/javascript">
    $("#btn4").click(function () {
        $("#v1").before("<p>btn4</p>");    //在被选中元素之前插入内容或者元素
    })
</script>
</body>
</html>
```

## 删除元素
```js
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <script src="/Web/static/js/jquery.min.js"></script>
</head>
<body>
<div id="v0">v0
    <div id="v1">v1
        <div id="v2">v2</div>
        <div id="v3">v3</div>
    </div>
    v0-end
</div>
<button id="btn1">删除被选元素及子元素</button>
<button id="btn2">删除被选元素的子元素</button>
<script type="text/javascript">
    $("#btn1").click(function () {
        $("#v1").remove() //删除被选元素及子元素
    })
</script>
<script type="text/javascript">
    $("#btn2").click(function () {
        $("#v1").empty()   //删除被选元素的子元素
    })
</script>
</body>
</html>
```

## 设置 CSS 样式
```js
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <script src="/Web/static/js/jquery.min.js"></script>
    <style>
        .cls{
            font-size: 32px;
        }
    </style>
</head>
<body>
<div id="v0">v0
    <div id="v1">v1
        <div id="v2">v2</div>
        <div id="v3">v3</div>
    </div>
    v0-end
</div>
<button id="btn1">btn1</button>
<button id="btn2">btn2</button>
<button id="btn3">btn3</button>
<button id="btn4">btn4</button>
<script type="text/javascript">
    $("#btn1").click(function () {
        $("#v1").css({"color":"red"}) //设置样式属性（键值）
    })
    $("#btn2").click(function () {
        $("#v1").addClass("cls")   //向被选元素添加一个或多个类样式
    })
    $("#btn3").click(function () {
        $("#v1").removeClass("cls")   //删除被选元素的子元素
    })
    $("#btn4").click(function () {
        $("#v1").toggleClass("cls")   //删除被选元素的子元素
    })
</script>
</body>
</html>
```