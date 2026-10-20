from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('accounts/register/', views.register, name='register'),
    path('attendance/add/', views.add_attendance, name='attendance_add'),
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('profile/', views.profile, name='profile'),
    path('attendance/stats/', views.attendance_stats, name='attendance_stats'),
    path('attendance/stats/by-name/', views.stats_absences_by_name, name='stats_by_name'),
    path('attendance/stats/by-count/', views.stats_absences_by_count, name='stats_by_count'),
    path('my-attendance/', views.my_attendance, name='my_attendance'),
    path('attendance/groups/', views.group_stats_view, name='group_stats'),

]