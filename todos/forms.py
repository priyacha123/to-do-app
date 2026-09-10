from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'due_date', 'category']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }