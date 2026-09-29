from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import calendar
from datetime import timedelta


PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
]

RECURRENCE_CHOICES = [
    ('none', 'Does not repeat'),
    ('daily', 'Daily'),
    ('weekly', 'Weekly'),
    ('monthly', 'Monthly'),
]

# Create your models here.
class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    recurrence = models.CharField(max_length=10, choices=RECURRENCE_CHOICES, default='none')
    reminder_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        if self.due_date and not self.completed:
            return self.due_date < timezone.now().date()
        return False

    @property
    def is_reminder_due(self):
        return bool(
            self.reminder_at
            and not self.completed
            and self.reminder_at <= timezone.now()
        )

    def next_due_date(self):
        if not self.due_date or self.recurrence == 'none':
            return None
        if self.recurrence == 'daily':
            return self.due_date + timedelta(days=1)
        if self.recurrence == 'weekly':
            return self.due_date + timedelta(weeks=1)
        month = self.due_date.month % 12 + 1
        year = self.due_date.year + (self.due_date.month // 12)
        days_in_month = calendar.monthrange(year, month)[1]
        return self.due_date.replace(year=year, month=month, day=min(self.due_date.day, days_in_month))