from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    name = models.CharField(max_length=50, verbose_name='姓名', blank=True)
    phone = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='注册时间')
    
    class Meta:
        app_label = 'user'  # 添加这一行，显式声明app_label
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return self.name or self.username
