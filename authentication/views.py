from django.shortcuts import render
from django.http import HttpResponseRedirect
from authentication.forms import *
from django.contrib.auth import authenticate
from django.contrib.auth import login as djangologin
from authentication.forms import LoginForm
from django.core.exceptions import ValidationError

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
        form = LoginForm()

    context = {
        'form': form,
    }

    return render(request, 'authentication/login.html', context)
