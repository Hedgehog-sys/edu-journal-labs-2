from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Attendance, Group

User = get_user_model()

class RegisterForm(UserCreationForm):
    email = forms.EmailField(label='Email', required=True)
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(), 
        label='Группа', 
        required=True,
        empty_label="Выбери свою группу"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'group')

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ('student', 'date', 'present')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }