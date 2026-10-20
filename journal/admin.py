

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Attendance, Group, Student, User, Teacher

admin.site.register(User, UserAdmin)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user_profile')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'user_profile__username')

class StudentInline(admin.TabularInline):
    model = Student
    extra = 1

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    inlines = (StudentInline,)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'group')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'group__name')
    list_filter = ('group',)

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'date', 'present')
    list_display_links = ('id', 'student')
    list_filter = ('present', 'student__group', 'date')
    search_fields = ('student__name',)
    ordering = ('-date', '-id')
    autocomplete_fields = ('student',)
    fields = ('student', 'date', 'present')
    actions = ('mark_as_present',)

    @admin.action(
        description='Отметить выбранные как присутствовавшие',
        permissions=['change'],
    )
    def mark_as_present(self, request, queryset):
        count = queryset.update(present=True)
        self.message_user(request, f'Обновлено записей: {count}')

admin.site.site_header = 'Электронный журнал - Администрирование'
admin.site.index_title = 'Административная панель'
admin.site.site_title = 'ЭЖ Админ'