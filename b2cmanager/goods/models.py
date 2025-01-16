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