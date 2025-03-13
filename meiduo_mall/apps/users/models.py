from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
class User(AbstractUser):
    mobile=models.CharField(max_length=11,default=0,unique=True)
    password2=models.CharField(max_length=10,default='1234567890')
    allow=models.BooleanField(default=True)
    class Meta:
        db_table = 'tb_users'
        verbose_name="用户管理"
        verbose_name_plural=verbose_name