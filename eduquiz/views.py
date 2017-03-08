from django.shortcuts import render
from quiz.models import *
from authentication.forms import RegistrationForm


def index(request):

    context = {
        'regForm': RegistrationForm(),
    }

    return render(request, 'eduquiz/index.html', context)
