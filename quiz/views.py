from django.shortcuts import render
from quiz.models import *


def question(request):

    question = MultipleChoiceQuestion.objects.all()[0]
    qts = QuestionTopic.objects.filter(question=question)
    topics = [qt.topic for qt in qts]
    answers = MultipleChoiceAnswer.objects.filter(question=question)

    context = {
        'question': question,
        'topics': topics,
        'answers': answers,
    }

    return render(request, 'quiz/multipleChoiceQuestion.html', context)
