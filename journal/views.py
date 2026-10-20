# Create your views here.

from django import forms
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.db.models import Count, Q
from .models import Attendance, Student, Group
from .forms import AttendanceForm, RegisterForm
from .decorators import teacher_required

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

@teacher_required
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

@login_required
def profile(request):
    if request.user.is_teacher():
        return redirect('home')
    
    student = (
        request.user.student_profile
        if request.user.is_student() else None
    )
    return render(
        request,
        'journal/profile.html',
        {'student': student},
    )


class PeriodForm(forms.Form):
    start_date = forms.DateField(label='Начало периода', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label='Конец периода', required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')
        if start and end and start > end:
            raise forms.ValidationError('Дата начала не может быть позже даты окончания!')
        return cleaned_data

@teacher_required
def attendance_stats(request):
    form = PeriodForm(request.GET or None)
    stats = None
    
    if form.is_valid():
        start = form.cleaned_data.get('start_date')
        end = form.cleaned_data.get('end_date')
        
        q_present = Q(attendance__present=True)
        q_absent = Q(attendance__present=False)
        
        if start:
            q_present &= Q(attendance__date__gte=start)
            q_absent &= Q(attendance__date__gte=start)
        if end:
            q_present &= Q(attendance__date__lte=end)
            q_absent &= Q(attendance__date__lte=end)
            
        stats = (
            Student.objects.select_related('group')
            .annotate(
                total=Count('attendance', filter=Q(attendance__date__range=(start, end)) if start and end else (Q(attendance__date__gte=start) if start else (Q(attendance__date__lte=end) if end else None))),
                attended=Count('attendance', filter=q_present),
                absences=Count('attendance', filter=q_absent),
            )
            .order_by('-absences', 'name', 'pk')
        )
        
        for student in stats:
            student.attendance_percent = (
                student.attended * 100 / student.total
                if student.total else None
            )
            
    return render(request, 'journal/stats.html', {'stats': stats, 'form': form})

@teacher_required
def stats_absences_by_name(request):
    stats = (
        Student.objects.select_related('group')
        .annotate(
            total=Count('attendance'),
            attended=Count('attendance', filter=Q(attendance__present=True)),
            absences=Count('attendance', filter=Q(attendance__present=False)),
        )
        .filter(absences__gt=5)
        .order_by('name')
    )
    return render(request, 'journal/stats_filtered.html', {'stats': stats, 'title': 'Сортировка по имени'})


@teacher_required
def stats_absences_by_count(request):
    stats = (
        Student.objects.select_related('group')
        .annotate(
            total=Count('attendance'),
            attended=Count('attendance', filter=Q(attendance__present=True)),
            absences=Count('attendance', filter=Q(attendance__present=False)),
        )
        .filter(absences__gt=5)
        .order_by('-absences')
    )
    return render(request, 'journal/stats_filtered.html', {'stats': stats, 'title': 'Сортировка по убыванию пропусков'})


@login_required
def my_attendance(request):
    if not request.user.is_student():
        return redirect('home')
    
    student_profile = request.user.student_profile
    attendances = Attendance.objects.filter(student=student_profile).order_by('-date')
    
    return render(
        request, 
        'journal/my_attendance.html', 
        get_context_with_menu(request, {'attendances': attendances})
    )


@teacher_required
def group_stats_view(request):
    group_stats = (
        Group.objects.annotate(
            student_count=Count('student', distinct=True),
            present_count=Count(
                'student__attendance',
                filter=Q(student__attendance__present=True),
            ),
        )
        .order_by('name', 'pk')
    )
    return render(
        request, 
        'journal/group_stats.html', 
        get_context_with_menu(request, {'group_stats': group_stats})
    )