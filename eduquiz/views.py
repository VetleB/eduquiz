from django.shortcuts import render
from quiz.models import *


def index(request):

    context = {
    }

    return render(request, 'eduquiz/index.html', context)
