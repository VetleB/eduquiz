from django.shortcuts import render
from authentication.forms import RegistrationForm


def index(request):

    context = {
        'form': RegistrationForm(),

    }

    return render(request, 'eduquiz/index.html', context)
