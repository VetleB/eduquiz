from django.shortcuts import render
from quiz.models import *


def index(request):

    topics = Topic.objects.all()
    subjects = Subject.objects.all()

    context = {
        'subjects': subjects,
        'topics': topics,
    }

    return render(request, 'eduquiz/index.html', context)
