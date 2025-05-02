from django.urls import path
from . import views

urlpatterns = [
    path('available-rooms/', views.available_rooms, name='available_rooms'),
    path('room-detail/<int:room_id>/', views.room_detail, name='room_detail'),
    path('create/', views.create_booking, name='create_booking'),
    path('list/', views.booking_list, name='booking_list'),
    path('update-status/<int:booking_id>/', views.update_booking_status, name='update_booking_status'),
    path('add-comment/<int:booking_id>/', views.add_comment, name='add_comment'),
    # 添加自助入住相关路由
    path('verify-check-in-code/', views.verify_check_in_code, name='verify_check_in_code'),
    path('confirm-check-in/', views.confirm_check_in, name='confirm_check_in'),
    path('check-out/', views.check_out, name='check_out'),
]