from django.contrib import admin
from .models import Room, RoomDetail, Booking

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'room_detail')
    search_fields = ('room_number',)
    list_filter = ('room_detail__room_type',)

@admin.register(RoomDetail)
class RoomDetailAdmin(admin.ModelAdmin):
    list_display = ('get_room_type_display', 'price')
    list_filter = ('room_type',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_number', 'customer', 'room', 'check_in_date', 'check_out_date', 'get_booking_status_display')
    list_filter = ('booking_status', 'check_in_date', 'check_out_date')
    search_fields = ('booking_number', 'guest_name', 'guest_phone', 'guest_id_card')
    date_hierarchy = 'check_in_date'
    readonly_fields = ('booking_number',)
