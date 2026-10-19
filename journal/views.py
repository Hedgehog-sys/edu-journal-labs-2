# Create your views here.

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from .forms import AttendanceForm, RegisterForm
from .models import Attendance, Student

def get_context_with_menu(request, extra_context=None):
    context = {
        'menu': [
            {'title': 'Главная', 'url_name': 'home'},
            {'title': 'О системе', 'url_name': 'about'},
            {'title': 'Контакты', 'url_name': 'contacts'},
            {'title': 'Регистрация', 'url_name': 'register'},
        ]
    }

    if request.user.is_authenticated:
        context['menu'].append({'title': 'Журнал', 'url_name': 'attendance_list'})






    
    if extra_context:
        context.update(extra_context)
    return context

def index(request):
    return render(
        request, 
        'journal/index.html', 
        get_context_with_menu(request, {'welcome': 'Добро пожаловать в систему!'})
    )

def about(request):
    return render(request, 'journal/about.html', get_context_with_menu(request))

def contacts(request):
    return render(request, 'journal/contacts.html', get_context_with_menu(request))

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            Student.objects.create(
                name=user.get_full_name() or user.username,
                group=form.cleaned_data['group'],
                user_profile=user,
            )
            
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'journal/register.html', get_context_with_menu(request, {'form': form}))

def is_teacher(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_teacher)
def add_attendance(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('attendance_list')
    else:
        form = AttendanceForm()
    return render(request, 'journal/add_attendance.html', get_context_with_menu(request, {'form': form}))

@login_required
def attendance_list(request):
    if request.user.is_staff:
        attendances = Attendance.objects.all().order_by('-date')
    else:
        if hasattr(request.user, 'student_profile'):
            attendances = Attendance.objects.filter(student=request.user.student_profile).order_by('-date')
        else:
            attendances = Attendance.objects.none()

    
    return render(
        request, 
        'journal/attendance_list.html', 
        get_context_with_menu(request, {'attendances': attendances})
    )