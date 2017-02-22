
from django.shortcuts import render
from authentication.forms import *


def login(request):
    context = {
    }
    if request.method=='POST':
        form = loginForm(request.POST)
    else:
        print("nope")

    return render(request, 'authentication/login.html', context)

