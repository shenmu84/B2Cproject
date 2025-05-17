# models.py
from django.db import models

class DateHourBehavior(models.Model):
    dates = models.CharField(max_length=10,primary_key=True)
    hours = models.CharField(max_length=2)    # 格式：'00' ~ '23'
    pv = models.IntegerField()                # 浏览行为数量
    cart = models.IntegerField()              # 加入购物车行为数量
    fav = models.IntegerField()               # 收藏行为数量
    buy = models.IntegerField()               # 购买行为数量

    class Meta:
        db_table = 'date_hour_behavior'
        verbose_name = '每小时用户行为数据'
        verbose_name_plural = '每小时用户行为数据'
        ordering = ['dates', 'hours']
        managed = False  # 告诉 Django 不要管理这个表（不创建、不修改）
        unique_together = ('dates', 'hours')  # 联合主键（模拟主键）

    def __str__(self):
        return f"{self.dates} {self.hours}:00 - PV: {self.pv}, Cart: {self.cart}, Fav: {self.fav}, Buy: {self.buy}"

class PathResult(models.Model):
    path_type = models.CharField(max_length=4,primary_key=True)
    description = models.CharField(max_length=40)
    num = models.IntegerField()
    class Meta:
        db_table = 'path_result'
        managed = False  # 告诉 Django 不要管理这个表（不创建、不修改）

class RFMModel(models.Model):
    user_id = models.BigIntegerField(primary_key=True)
    frequency = models.IntegerField()
    recent = models.DateField()
    fscore = models.IntegerField()
    rscore = models.IntegerField()
    class_field = models.CharField(max_length=20, db_column='class')  # 避免 Python 保留字冲突

    class Meta:
        db_table = 'rfm_model'
        managed = False  # 告诉 Django 不要管理这个表（不创建、不修改）


