from django.shortcuts import render
from authentication.forms import RegistrationForm


def index(request):

    context = {
        'regForm': RegistrationForm(),
    }

    return render(request, 'eduquiz/index.html', context)
