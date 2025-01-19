from django.db import models

# Create your models here.
class Good(models.Model):
    name = models.CharField(max_length=10)
    def __str__(self):
        return self.name
class User(models.Model):
    name = models.CharField(max_length=10)
    gender = models.CharField(max_length=1)
    #外键约束买家买了什么东西
    book=models.ForeignKey(Good, on_delete=models.CASCADE)

class GoodInfo(models.Model):
    name = models.CharField(max_length=10,unique=True)
    pub_date = models.DateField(null=True)
    readcount=models.IntegerField(default=0)
    commentcount=models.IntegerField(default=0)
    is_delete=models.BooleanField(default=False)
    class Meta:
        #修改表的名字
        db_table='goodinfo'
        #admin站点使用的
        verbose_name="货物管理"
class UserInfo(models.Model):
    GENDER_CHOICES = (
        (1,'male'),
        (2,'female')
    )
    name=models.CharField(max_length=10,unique=True)
    gendere=models.SmallIntegerField(choices=GENDER_CHOICES,default=1)
    description=models.CharField(max_length=100,null=True)
    is_delete=models.BooleanField(default=False)

    #系统自动添加外键
    good=models.ForeignKey(GoodInfo,on_delete=models.CASCADE)
    class Meta:
        db_table='userinfo'
