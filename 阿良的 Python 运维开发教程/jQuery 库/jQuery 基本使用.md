# jQuery 基本使用
- jQuery 是一个 JavaScript 库，极大地简化了 JavaScript 编程
- 一般采用 1.x 版本，比较常用

## jQuery 语法
### 实现按钮弹窗提示功能
- JavaScript 语法
    ```js
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Title</title>
    </head>
    <body>
    <button type="button" id="btn">点我</button>
    <script type="text/javascript">
        var x = document.getElementById("btn")
        x.onclick = function () {
            alert('亲，有什么可以帮你的？')
        }
    </script>
    </body>
    </html>
    ```
- JQuery 语法
    ```js
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Title</title>
        <script src="/Web/static/js/jquery.min.js"></script>
    </head>
    <body>
    <button type="button" id="btn">点我</button>
    <script type="text/javascript">
        $('#btn').click(function () {
            alert('ok')
        })
    </script>
    </body>
    </html>
    ```

## 选择器
### 标签选择器
- 语法： element
- 示例： 选取所有 h2 元素
    ```js
    $("h2")
    ```
### 类选择器
- 语法： .class
- 示例： 选取所有 class 为 title 的元素
    ```js
    $(".title")
    ```
### id 选择器
- 语法： #id
- 示例： 选取所有 id 为 title 的元素
    ```js
    $("#title")
    ```
### 并集选择器
- 语法： selector1,selector2,...
- 示例： 选取所有 div , p 和用法有class 为 title 的元素
    ```js
    $("div,p,.title")
    ```
### 属性选择器
- 示例：选取 input 标签名为 username 的元素
    ```js
    $("input[name]= 'username'")
    ```
- 示例：选取 href 值等于 "#" 的元素
    ```js
    $("[href= '#']")
    ```