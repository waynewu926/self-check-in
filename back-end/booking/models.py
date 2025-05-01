from django.db import models
from django.contrib.auth.models import User
import random
import string
import uuid
# Create your models here.

class Room(models.Model):
    room_number = models.CharField(max_length=3, unique=True)
    room_detail = models.ForeignKey('RoomDetail', on_delete=models.CASCADE, related_name='rooms')

    def __str__(self):
        return f"{self.room_number} - {self.room_detail.get_room_type_display()}"

class RoomDetail(models.Model):
    room_type = models.IntegerField(choices=[
        (1, '标准间'),
        (2, '豪华间'),
        (3, '套房'),
    ], unique=True)    
    price = models.IntegerField()
    
    def __str__(self):
        return f"{self.get_room_type_display()} 详情"

class Booking(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    booking_number = models.CharField(max_length=7, unique=True)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    booking_status = models.IntegerField(choices=[
        (0, '已取消'),
        (1, '待入住'),
        (2, '已入住'),
        (3, '已完成'),
    ])
    guest_name = models.CharField(max_length=50)
    guest_phone = models.CharField(max_length=11)
    guest_id_card = models.CharField(max_length=18)
    guest_count = models.IntegerField(default=1) 
    code = models.CharField(max_length=4, blank=True, null=True)
    room_password = models.CharField(max_length=6, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    comment_time = models.DateTimeField(blank=True, null=True)

    def generate_booking_number(self):
        """生成订单号：R + 6位数字"""
        self.booking_number = f"R{uuid.uuid4().hex[:6].upper()}"
        self.save(update_fields=['booking_number'])
        return self.booking_number
    
    def generate_code(self):
        """生成4位数字验证码"""
        self.code = ''.join(random.choices(string.digits, k=4))
        self.save(update_fields=['code'])
        return self.code
    
    def generate_room_password(self):
        """生成6位数字房间密码"""
        self.room_password = ''.join(random.choices(string.digits, k=6))
        self.save(update_fields=['room_password'])
        return self.room_password

    @classmethod
    def is_room_available(cls, room_id, check_in_date, check_out_date):
        """检查房间在指定日期范围内是否可用"""
        # 使用一个更高效的查询
        overlapping_bookings = cls.objects.filter(
            room_id=room_id,
            booking_status__in=[1, 2],  # 待入住或已入住
            check_in_date__lt=check_out_date,  # 入住日期早于查询的退房日期
            check_out_date__gt=check_in_date   # 退房日期晚于查询的入住日期
        )
        
        # 如果存在重叠的预订，则房间不可用
        return not overlapping_bookings.exists()

    @property
    def total_price(self):
        """计算预订总价"""
        from datetime import timedelta
        days = (self.check_out_date - self.check_in_date).days
        price_per_day = self.room.room_detail.price
        return price_per_day * days

    def __str__(self):
        return f"Booking {self.booking_number} by {self.customer}"

    class Meta:
        indexes = [
            models.Index(fields=['room']),
            models.Index(fields=['check_in_date']),
            models.Index(fields=['check_out_date']),
            models.Index(fields=['booking_status']),
            models.Index(fields=['room', 'booking_status']),
            models.Index(fields=['check_in_date', 'check_out_date']),
            # 添加更高效的复合索引
            models.Index(fields=['room', 'booking_status', 'check_in_date', 'check_out_date'], name='booking_search_idx'),
        ]
    

