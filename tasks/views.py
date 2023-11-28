from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError

# Para el registro de usuarios.
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Formularios custom
from .forms import TaskForm

# Modelos de datos
from .models import Task


# Create your views here.
def home(request):
    return render(request, "tasks/home.html")


def signup(request):
    if request.method == "GET":
        return render(request, "tasks/signup.html", {"form": UserCreationForm})
    else:
        # Si las contraseñas coinciden, se registra al usuario. Caso contrario, se genera un mensaje
        # que diga que las contraseñas no coinciden.
        if request.POST["password1"] == request.POST["password2"]:
            try:
                new_user = User.objects.create_user(
                    username=request.POST["username"],
                    password=request.POST["password1"],
                )
                new_user.save()
                login(request, new_user)
                return redirect("tasks")
            except IntegrityError:
                return render(
                    request,
                    "tasks/signup.html",
                    {"form": UserCreationForm, "error": "User already exists"},
                )
        return render(
            request,
            "tasks/signup.html",
            {"form": UserCreationForm, "error": "Passwords do not match!"},
        )


@login_required
def tasks(request):
    # Solo dame las tareas del usuario actual, y aquellas que no tienen una fecha de
    # finalización (las que aun no ha completado).
    tasks = Task.objects.filter(user=request.user, date_completed__isnull=True)
    return render(request, "tasks/tasks.html", {"tasks": tasks})


@login_required
def tasks_completed(request):
    # Solo dame las tareas del usuario actual, y aquellas que no tienen una fecha de
    # finalización (las que aun no ha completado).
    tasks = Task.objects.filter(
        user=request.user, date_completed__isnull=False
    ).order_by("-date_completed")
    return render(request, "tasks/tasks.html", {"tasks": tasks})


@login_required
def create_task(request):
    if request.method == "GET":
        return render(request, "tasks/create_task.html", {"form": TaskForm})
    else:
        try:
            # Se crea un form con los datos dados por el usuario
            form = TaskForm(request.POST)
            # Se guardan los datos en una nueva instancia del objeto, pero sin hacer
            # commit a base de datos aún.
            new_task = form.save(commit=False)
            # Se asigna el usuario que creo la task.
            new_task.user = request.user
            new_task.save()
            return redirect("tasks")
        except ValueError:
            return render(
                request,
                "tasks/create_task.html",
                {"form": TaskForm, "error": "Please provide valid data"},
            )


@login_required
def task_detail(request, task_id):
    if request.method == "GET":
        # Getting the task that corresponds to the given ID.
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        # Creating a form to update a Task, with the data from said task.
        form = TaskForm(instance=task)
        return render(request, "tasks/task_detail.html", {"task": task, "form": form})
    else:
        try:
            # Getting the task that corresponds to the given ID.
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect("tasks")
        except ValueError:
            return render(
                request,
                "tasks/task_detail.html",
                {"task": task, "form": form, "error": "Error updating task"},
            )


@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == "POST":
        task.date_completed = timezone.now()
        task.save()
        return redirect("tasks")


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == "POST":
        task.delete()
        return redirect("tasks")


@login_required
def signout(request):
    logout(request)
    return redirect("home")


def signin(request):
    if request.method == "GET":
        return render(request, "tasks/signin.html", {"form": AuthenticationForm})
    else:
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"],
        )
        if not user:
            return render(
                request,
                "tasks/signin.html",
                {
                    "form": AuthenticationForm,
                    "error": "Username or password is incorrect.",
                },
            )
        else:
            login(request, user)
            return redirect("tasks")
