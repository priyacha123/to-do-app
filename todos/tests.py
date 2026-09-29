from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Category, Task


class TaskFeatureTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='feature-user', password='test-pass-123')
        self.client.login(username='feature-user', password='test-pass-123')
        self.category = Category.objects.create(user=self.user, name='Work')

    def test_dashboard_filters_today_tasks(self):
        Task.objects.create(user=self.user, title='Today', due_date=date.today())
        Task.objects.create(user=self.user, title='Tomorrow', due_date=date.today() + timedelta(days=1))

        response = self.client.get(reverse('task_list'), {'status': 'today'})

        self.assertContains(response, 'Today')
        self.assertNotContains(response, 'Tomorrow')

    def test_dashboard_shows_category_count(self):
        Task.objects.create(user=self.user, title='Task', category=self.category)

        response = self.client.get(reverse('task_list'))

        self.assertContains(response, 'Work')
        self.assertContains(response, '>1</strong>')

    def test_completing_recurring_task_creates_next_task(self):
        task = Task.objects.create(
            user=self.user,
            title='Weekly review',
            due_date=date.today(),
            recurrence='weekly',
            priority='high',
        )

        self.client.post(reverse('task_toggle', args=[task.pk]))

        self.assertTrue(Task.objects.get(pk=task.pk).completed)
        self.assertTrue(Task.objects.filter(
            title='Weekly review',
            due_date=date.today() + timedelta(weeks=1),
            recurrence='weekly',
            priority='high',
            completed=False,
        ).exists())

    def test_completing_reminder_task_does_not_create_task(self):
        task = Task.objects.create(
            user=self.user,
            title='Reminder only',
            due_date=date.today(),
            reminder_at='2026-09-29T10:00:00Z',
            recurrence='none',
        )

        self.client.post(reverse('task_toggle', args=[task.pk]))

        self.assertEqual(Task.objects.filter(title='Reminder only').count(), 1)
        self.assertTrue(Task.objects.get(pk=task.pk).completed)

    def test_toggle_get_does_not_change_task(self):
        task = Task.objects.create(user=self.user, title='Post only')

        self.client.get(reverse('task_toggle', args=[task.pk]))

        self.assertFalse(Task.objects.get(pk=task.pk).completed)

    def test_reminder_prevents_recurring_follow_up_task(self):
        task = Task.objects.create(
            user=self.user,
            title='Reminder and recurrence',
            due_date=date.today(),
            reminder_at='2026-09-29T10:00:00Z',
            recurrence='weekly',
        )

        self.client.post(reverse('task_toggle', args=[task.pk]))

        self.assertEqual(Task.objects.filter(title='Reminder and recurrence').count(), 1)
        self.assertTrue(Task.objects.get(pk=task.pk).completed)
