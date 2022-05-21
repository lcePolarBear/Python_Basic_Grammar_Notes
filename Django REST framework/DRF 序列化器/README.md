# DRF 序列化器

## 序列化与反序列化

### JSON 序列化

```python
import json
# 序列化
computer = {"主机":5000,"显示器":1000,"鼠标":60,"键盘":150}

json.dumps(computer)

# 反序列化
json.loads(json_obj)
```

### Django 内置 Serializers 模块

Serializers 是 Django 内置的一个序列化器，可直接将 Python 对象转为 JSON 格式，但不支
持反序列化

```python
from django.core import serializers

obj = User.objects.all()

data = serializers.serialize('json', obj)
```

### Django 内置 JsonResponse 模块

JsonResponse 模块自动将 Python 对象转为 JSON 对象并响应

## DRF 序列化器

DRF 中有一个 serializers 模块专门负责数据序列化，DRF 提供了更先进、更高级别的序列化方案

### 序列化器支持三种类型

1. **Serializer** ：对Model（数据模型）进行序列化，需自定义字段映射
2. **ModelSerializer** ：对Model进行序列化，会自动生成字段和验证规则，默认还包含简单的create()和update()方法
3. **HyperlinkedModelSerializer** ：与ModelSerializer类似，只不过使用超链接来表示关系而不是主键ID

## Serializer

[使用 Serializer 操作数据](./%E4%BD%BF%E7%94%A8%20Serializer%20%E6%93%8D%E4%BD%9C%E6%95%B0%E6%8D%AE.md)

### 序列化器工作流程

1. **序列化（读数据）**

视图里通过 ORM 从数据库获取数据查询集对象 → 数据传入序列化器 → 序列化器将数据进行序列化 → 调用序列化器的.data获取数据 → 响应返回前端

1. **反序列化（写数据）**

视图获取前端提交的数据 → 数据传入序列化器 → 调用序列化器的.is_valid方法进行效验 → 调用序列化器的.save()方法保存数据

### 序列化器常用方法与属性

1. serializer.is_valid()

调用序列化器验证是否通过，传入 raise_exception=True 可以在验证失败时由 DRF 响应 400 异常

1. serializer.errors()

获取反序列化器验证的错误信息

1. serializer.data()

获取序列化器返回的数据

1. serializer.save()

将验证通过的数据保存到数据库（ORM操作）