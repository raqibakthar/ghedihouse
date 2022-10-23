from csv import list_dialects
from django.contrib import admin
from .models import Account, UserProfile

# Register your models here.

class AccountAdmin(admin.ModelAdmin):
    list_display = ('email','first_name','last_name','username','last_login','date_joined','is_active')

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user','city','state','country')

admin.site.register(Account,AccountAdmin)
admin.site.register(UserProfile,UserProfileAdmin)