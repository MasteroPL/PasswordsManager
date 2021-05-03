from django.contrib import admin
from main.models import (
	Password,
	UserPasswordAssignment
)

# Register your models here.
class PasswordAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'description', 'owner', 'created_by', 'created_at', 'updated_by', 'updated_at')

admin.site.register(Password, PasswordAdmin)


class UserPasswordAssignmentAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'password')

admin.site.register(UserPasswordAssignment, UserPasswordAssignmentAdmin)