import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from bos.models import *
from django.contrib.auth.models import User


def logout_view(request):
    logout(request)
    return redirect(login_view)


# @login_required
def index(request):
    return render(request, 'index.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('user', '')
        password = request.POST.get('contrasenia', '')
        user = authenticate(username=username, password=password)
        if not user:
            return render(request, 'login.html', {'login_incorrect': True})
        else:
            login(request, user)
            return redirect(index)

    if request.user.is_authenticated and not request.user.is_anonymous():
        return redirect(index)
    else:
        return render(request, 'login.html', {'login_incorrect': False})


def register_view(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    else:
        user = User()
        user.name = request.POST.get('empleado[first_name]', ' ')
        user.last_name = request.POST.get('empleado[last_name]', ' ')
        user.email = request.POST.get('empleado[email]', ' ')
        user.set_password(request.POST.get('empleado[password]', ' '))
        user.save()
        empleado = Empleado(name=user.name, apellido=user.last_name,
                            user=user)
        empleado.save()

        return redirect(index)
