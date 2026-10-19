

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Attendance, Group, Student, User


admin.site.register(User, UserAdmin)
admin.site.register(Group)
admin.site.register(Student)
admin.site.register(Attendance)