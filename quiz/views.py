from django.shortcuts import render
from quiz.models import MultipleChoiceQuestion


def question(request):

    context = {
        question: MultipleChoiceQuestion.objects.order_by('?').first(),
    }

    return render(request, 'quiz/question.html', context)
