from django.shortcuts import render
from django.http import HttpResponseRedirect
from authentication.forms import *
from django.contrib import messages
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth import login as djangologin
from authentication.forms import LoginForm, RegistrationForm
from django.contrib.auth import logout as djangologout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.admin import User
from quiz.models import Player, PlayerRating, Subject


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
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')

    top_pr = PlayerRating.objects.filter(player=Player.objects.get(user=request.user)).order_by('-rating').first()

    player_subjects = request.user.player.subjectAnswers()
    try:
        fav_sub = Subject.objects.get(title=player_subjects[1][player_subjects[0].index(max(player_subjects[0]))])
    except ValueError:
        fav_sub = None

    context = {
        'top_pr': top_pr,
        'fav_sub': fav_sub,
        'login_form': None,
        'name_form': None,
    }

    return render(request, 'authentication/account.html', context)


def change_pswd(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!

            messages.success(request, 'Your password was successfully updated!')
            return HttpResponseRedirect('/authentication/account/')
    else:
        form = PasswordChangeForm(
            user=request.user.player,
        )

    context = {
        'login_form': form,
    }
    return render(request, 'authentication/account.html', context)


def change_name(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        form = ChangeUsernameForm(request.user, request.POST)
        if form.is_valid():
            userdict = form.cleaned_data
            user = request.user
            user.username = userdict['username']
            user.save()

            messages.success(request, 'Your username was successfully updated!')
            return HttpResponseRedirect('/authentication/account/')
    else:
        form = ChangeUsernameForm(
            user=request.user,
        )

    context = {
        'name_form': form,
    }
    return render(request, 'authentication/account.html', context)
