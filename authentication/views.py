from django.shortcuts import render
from django.http import HttpResponseRedirect
from authentication.forms import *
from django.contrib.auth import authenticate
from django.contrib.auth import login as djangologin
from authentication.forms import LoginForm, RegistrationForm
from django.contrib.auth import logout as djangologout
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
    return HttpResponseRedirect("/")


def register(request):
    if request.method == 'POST':
        print(request.POST)
        form = RegistrationForm(request.POST)

        if form.is_valid():
            #Dictionary to hold user information
            userDict=form.cleaned_data
            user=User.objects.create_user(
                username=userDict['username'],
                password=userDict['password'],
                first_name=userDict['firstName'],
                last_name=userDict['lastName'],
                email=userDict['email'],
            )
            user.save()
            new_user=authenticate(username=form.cleaned_data["username"],
                                  password=form.cleaned_data["password"])
            player=Player(user=user)
            player.save()
            login(request)


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
    return render(request, 'authentication/ account.html', {})
