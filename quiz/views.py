from django.http import JsonResponse
from django.shortcuts import render
from quiz.models import *
import random


def question(request):
    if request.method == 'POST':

        questionID = eval(request.POST['question'])

        question = (list(TrueFalseQuestion.objects.filter(id=questionID))
            + list(MultipleChoiceQuestion.objects.filter(id=questionID))
            + list(TextQuestion.objects.filter(id=questionID)))[0]

        if isinstance(question, MultipleChoiceQuestion):
            return question.answerFeedback(int(request.POST['answer']))

        elif isinstance(question, TrueFalseQuestion):
            return question.answerFeedback(eval(request.POST['answer']))

        elif isinstance(question, TextQuestion):
            return question.answerFeedback(request.POST['answer'])

        return JsonResponse({
        }, safe=False)

    else:
        r = random.random()
        if r > 2/3:
            return multipleChoiceQuestion(request, None)
        elif r > 1/3:
            return textQuestion(request, None)
        else:
            return trueFalseQuestion(request, None)


def multipleChoiceQuestion(request, question):

    ## REMOVE LATER
    questions = MultipleChoiceQuestion.objects.all()
    question = questions[random.randint(0, len(questions)-1)]
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
    questions = TrueFalseQuestion.objects.all()
    question = questions[random.randint(0, len(questions) - 1)]
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


def textQuestion(request, question):

    ## REMOVE LATER
    questions = TextQuestion.objects.all()
    question = questions[random.randint(0, len(questions) - 1)]
    # END

    qts = QuestionTopic.objects.filter(question=question)
    topics = [qt.topic for qt in qts]
    answers = question.answer

    context = {
        'question': question,
        'topics': topics,
        'answer': answers,
    }

    return render(request, 'quiz/textQuestion.html', context)
