from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'name', 'phone')
    search_fields = ('username', 'name', 'phone')

admin.site.register(User, UserAdmin)
