from django.db import models

# Create your models here.

class Customer(models.Model):
    name = models.CharField(max_length=20)
    phone = models.CharField(max_length=11, unique=True)  # 手机号唯一
    password = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)  # 注册时间自动生成

    def __str__(self):
        return self.name