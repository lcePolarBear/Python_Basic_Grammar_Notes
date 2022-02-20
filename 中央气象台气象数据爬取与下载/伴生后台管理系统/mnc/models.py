from django.db import models

# Create your models here.
class Taglist(models.Model):
    # 定义一对多模型关系
    tagid = models.AutoField(primary_key=True)
    label = models.CharField(max_length=30, null=True, verbose_name="数据源类型")
    attr_key = models.CharField(max_length=30, null=True, verbose_name="属性键")
    attr_value = models.CharField(max_length=30, null=True, verbose_name="属性值")
    src = models.CharField(max_length=30, verbose_name="目标值")
    datatime = models.DateTimeField(auto_now=True, verbose_name="创建日期")

    def __str__(self):
        return str(self.tagid)

    class Meta:
        db_table = 'Taglist'
        verbose_name_plural = '数据源 html 属性获取表'

class Urllist(models.Model):
    urlid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, unique=True, verbose_name="存储名称")
    type = models.CharField(max_length=30, null=True, verbose_name="气象类型")
    area = models.CharField(max_length=30, null=True, verbose_name="地区")
    para = models.CharField(max_length=30,verbose_name="参数")
    url = models.URLField(max_length=200, null=True, verbose_name="网址源")
    frequency = models.FloatField(max_length=30,verbose_name="刷新频率")
    table_name = models.CharField(max_length=30, null=True, verbose_name="数据源关联的数据存储表")
    taglist = models.ForeignKey(Taglist, on_delete=models.CASCADE)
    datatime = models.DateTimeField(auto_now_add=True,verbose_name="创建日期")

    def __str__(self):
        return str(self.urlid)

    class Meta:
        db_table = 'Urllist'
        verbose_name_plural = '数据源 URl 获取表'

