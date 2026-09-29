from django.shortcuts import render, redirect, get_object_or_404 
from .models import Category, Task
from .forms import CategoryForm, TaskForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Case, Count, IntegerField, Value, When
from django.utils import timezone

# Create your views here.
@login_required
def task_list(request):
    all_tasks = Task.objects.filter(user=request.user)
    tasks = all_tasks
    # render(request, template_path, context_dict)
    # The key 'tasks' is the variable name you'll use inside the HTML.
    query = request.GET.get('q')
    if query:
        tasks = tasks.filter(title__icontains=query)

    category_id = request.GET.get('category')
    if category_id:
        tasks = tasks.filter(category_id=category_id)

    status = request.GET.get('status', 'active')
    if status == 'active':
        tasks = tasks.filter(completed=False)
    elif status == 'completed':
        tasks = tasks.filter(completed=True)
    elif status == 'overdue':
        tasks = tasks.filter(completed=False, due_date__lt=timezone.now().date())
    elif status == 'today':
        tasks = tasks.filter(due_date=timezone.now().date())

    sort = request.GET.get('sort', 'newest')
    sort_fields = {
        'due_asc': ('due_date', '-created_at'),
        'due_desc': ('-due_date', '-created_at'),
        'newest': ('-created_at',),
    }
    if sort == 'priority':
        tasks = tasks.annotate(
            priority_order=Case(
                When(priority='high', then=Value(3)),
                When(priority='medium', then=Value(2)),
                When(priority='low', then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by('-priority_order', '-created_at')
    else:
        tasks = tasks.order_by(*sort_fields.get(sort, sort_fields['newest']))

    paginator = Paginator(tasks, 5)  # 5 tasks per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(user=request.user).annotate(task_count=Count('task'))
    total_tasks = all_tasks.count()
    completed_tasks = all_tasks.filter(completed=True).count()
    pending_tasks = total_tasks - completed_tasks
    overdue_tasks = all_tasks.filter(
        completed=False,
        due_date__lt=timezone.now().date(),
    ).count()
    reminder_tasks = all_tasks.filter(
        completed=False,
        reminder_at__lte=timezone.now(),
    ).count()
    progress = round((completed_tasks / total_tasks) * 100) if total_tasks else 0

    return render(request, 'todos/task_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'overdue_tasks': overdue_tasks,
        'progress': progress,
        'status': status,
        'sort': sort,
        'reminder_tasks': reminder_tasks,
    })

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        form.fields['category'].queryset = Category.objects.filter(user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            # after saving, redirect the browser to the task_list URL (remember that name='task_list' in urls.py) 
            return redirect('task_list')
    else:
        form = TaskForm()
        form.fields['category'].queryset = Category.objects.filter(user=request.user)
    return render(request, 'todos/task_form.html', {'form': form})

@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        # Passing instance=task tells the form "you're not creating a new row, you're editing this specific existing one." When you call form.save(), Django updates that row instead of inserting a new one.
        form = TaskForm(request.POST, instance=task)
        form.fields['category'].queryset = Category.objects.filter(user=request.user)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
        form.fields['category'].queryset = Category.objects.filter(user=request.user)
    return render(request, 'todos/task_form.html', {'form': form})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')
    return render(request, 'todos/task_confirm_delete.html', {'task': task})

@login_required
def task_toggle(request, pk):
    if request.method != 'POST':
        return redirect('task_list')

    task = get_object_or_404(Task, pk=pk, user=request.user)
    was_completed = task.completed
    task.completed = not task.completed
    task.save()

    # A reminder never creates another task. Only an explicitly recurring
    # task with a due date gets its next occurrence.
    if (
        not was_completed
        and task.completed
        and task.due_date
        and not task.reminder_at
        and task.recurrence in {'daily', 'weekly', 'monthly'}
    ):
        next_due_date = task.next_due_date()
        if next_due_date:
            Task.objects.create(
                user=task.user,
                category=task.category,
                title=task.title,
                due_date=next_due_date,
                priority=task.priority,
                recurrence=task.recurrence,
            )
    return redirect('task_list')


@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            return redirect('task_list')
    else:
        form = CategoryForm()
    return render(request, 'todos/category_form.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'todos/signup.html', {'form': form})
