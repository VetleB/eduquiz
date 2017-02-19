from django.shortcuts import render
from quiz.models import *


def question(request):
    return trueFalseQuestion(request, None)
    #return multipleChoiceQuestion(request, None)


def multipleChoiceQuestion(request, question):

    ## REMOVE LATER
    question = MultipleChoiceQuestion.objects.all()[0]
    # END

    qts = QuestionTopic.objects.filter(question=question)
    topics = [qt.topic for qt in qts]
    answers = MultipleChoiceAnswer.objects.filter(question=question)

    context = {
        'question': question,
        'topics': topics,
        'answers': answers,
    }

    return render(request, 'quiz/multipleChoiceQuestion.html', context)


def trueFalseQuestion(request, question):

    # REMOVE LATER
    question = TrueFalseQuestion.objects.all()[0]
    # END

    qts = QuestionTopic.objects.filter(question=question)
    topics = [qt.topic for qt in qts]
    answers = ('True', 'False')

    context = {
        'question': question,
        'topics': topics,
        'answers': answers,
    }

    return render(request, 'quiz/trueFalseQuestion.html', context)
