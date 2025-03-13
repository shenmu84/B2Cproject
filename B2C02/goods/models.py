from django.db import models
'''
id系统默认有
默认表的名字 子应用名_类名 小写
Object-Relational Mapping对象关系映射
ORM         DB
类           数据表
对象          数据行
属性          字段
'''
# Create your models here.
class GoodInfo(models.Model):
    #属性名对应mysql = mysql类型
    name=models.CharField(max_length=100,unique=True)
    pub_date=models.DateField(null=True)
    #阅读量
    readcount=models.IntegerField(default=0)
#评论数
    commentcount=models.IntegerField(default=0)

    is_deleted=models.BooleanField(default=False)
    class Meta:
        db_table='goodsinfo'#修改表的名称
        verbose_name="书籍管理"#admin站点使用的
    def __str__(self):
        return self.name
class PeopleInfo(models.Model):
    #定义一个有序字典
    GENDER_CHAOICE=(
        1,'males',
        2,'females'
    )
    name=models.CharField(max_length=100,unique=True)
    gender=models.CharField(max_length=11)
    description=models.TextField(max_length=100,null=True)
    is_deleted=models.BooleanField(default=False)

    book=models.ForeignKey(GoodInfo,on_delete=models.CASCADE)
    class Meta:
        db_table='peopleinfo'
    def __str__(self):
        return self.name
