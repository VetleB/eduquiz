from django.shortcuts import render
from django.http import HttpResponseRedirect
from authentication.forms import *
from django.contrib import messages
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth import login as djangologin
from authentication.forms import LoginForm, RegistrationForm
from django.contrib.auth import logout as djangologout
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from quiz.models import Player


def login(request):

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username = form.cleaned_data['username'],
                password = form.cleaned_data['password'],
            )
            if user is not None:
                djangologin(request, user)
                return HttpResponseRedirect('/')
    else:
        form = LoginForm(initial={
            'username': '',
        })

    context = {
        'form': form,
    }

    return render(request, 'eduquiz/index.html', context)


def logout(request):
    djangologout(request)
    return HttpResponseRedirect('/')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            #Dictionary to hold user information
            userDict = form.cleaned_data

            user = User.objects.create_user(
                username=userDict['username'],
                password=userDict['password'],
                first_name=userDict['firstName'],
                last_name=userDict['lastName'],
                email=userDict['email'],
            )

            Player.objects.create(user=user)
            login(request)

            return HttpResponseRedirect('/')

    else:
        form = RegistrationForm(initial={
            'username': '',
            'firstName': '',
            'email': '',
            'lastName': '',
        })

    context = {
        'regForm': form,
    }

    return render(request, 'eduquiz/index.html', context)


def account(request):
    context = {
        'login_form': None
    }

    return render(request, 'authentication/account.html', context)


def change_pswd(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')

            return account(request)
    else:
        form = PasswordChangeForm(
            user=request.user.player,
        )

    context = {
        'login_form': form,
    }
    return render(request, 'authentication/account.html', context)
