from django import forms
from .models import Category, Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'category', 'priority', 'due_date', 'reminder_at', 'recurrence']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'reminder_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        labels = {'name': 'Category name'}
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g. Work, Personal, Errands',
            }),
        }