from django.shortcuts import render, redirect, get_object_or_404 
from .models import Category, Task
from .forms import TaskForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

# Create your views here.
@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)
    # render(request, template_path, context_dict)
    # The key 'tasks' is the variable name you'll use inside the HTML.
    query = request.GET.get('q')
    if query:
        tasks = tasks.filter(title__icontains=query)

    category_id = request.GET.get('category')
    if category_id:
        tasks = tasks.filter(category_id=category_id)

    tasks = tasks.order_by('-created_at')

    paginator = Paginator(tasks, 5)  # 5 tasks per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(user=request.user)
    return render(request, 'todos/task_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
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
    task = get_object_or_404(Task, pk=pk, user=request.user) 
    task.completed = not task.completed
    task.save()
    return redirect('task_list')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'todos/signup.html', {'form': form})

