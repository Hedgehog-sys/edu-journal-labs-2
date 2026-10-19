from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('accounts/register/', views.register, name='register'),
    path('attendance/add/', views.add_attendance, name='attendance_add'),
    path('attendance/', views.attendance_list, name='attendance_list'),
]