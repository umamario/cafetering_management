import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from bos.models import *
from django.contrib.auth.models import User


def logout_view(request):
    logout(request)
    return redirect(login_view)


@login_required
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

# def register_view(request):
#     from cafetering_app.forms import RegistrationForm
#     if request.method == 'GET':
#         form = RegistrationForm()
#         return render(request, 'registration.html', {'form': form})
#     else:
#         form = RegistrationForm(request.POST)
#         if form.is_valid():
#             profile = Profile()
#             # trade.created_time = datetime.datetime.now()
#             profile.birth_date = form.cleaned_data['birth_date']
#             profile.gender = form.cleaned_data['gender']
#             profile.level_study = form.cleaned_data['level_study']
#             profile.name = form.cleaned_data['name']
#             profile.status = form.cleaned_data['status']
#             email = form.cleaned_data['email']
#             password = User.objects.make_random_password()
#             user = User.objects.create(username=email,
#                                        email=email, password=password)
#             profile.user = user
#             profile.save()
#
#             return redirect(index)
#         else:
#             return render(request, 'new_trade.html', {'form': form})
