from django.http import JsonResponse
from django.shortcuts import render
from quiz.models import *
import random


def question(request):
    if request.method == 'POST':

        questionID = eval(request.POST['question'])

        question = (list(TrueFalseQuestion.objects.filter(id=questionID))
            + list(MultipleChoiceQuestion.objects.filter(id=questionID))
            + list(TextQuestion.objects.filter(id=questionID))
            + list(NumberQuestion.objects.filter(id=questionID)))[0]

        feedback = {}
        if isinstance(question, MultipleChoiceQuestion):
            feedback = question.answerFeedback(int(request.POST['answer']))

        elif isinstance(question, TrueFalseQuestion):
            feedback = question.answerFeedback(eval(request.POST['answer']))

        elif isinstance(question, TextQuestion):
            feedback = question.answerFeedback(request.POST['answer'])

        elif isinstance(question, NumberQuestion):
            feedback = question.answerFeedback(request.POST['answer'])

        if hasattr(request, 'user') and hasattr(request.user, 'player') and feedback:
            result = feedback['answeredCorrect']
            PlayerAnswer(player=request.user.player, question=question, result=result).save()
            request.user.player.update(question, result)

        return JsonResponse(feedback, safe=False)

    else:
        r = random.random()
        if r > 3/4:
            return multipleChoiceQuestion(request, None)
        elif r > 2/4:
            return textQuestion(request, None)
        elif r > 1/4:
            return trueFalseQuestion(request, None)
        else:
            return numberQuestion(request, None)

def multipleChoiceQuestion(request, question):

    ## REMOVE LATER
    questions = MultipleChoiceQuestion.objects.all()
    question = questions[random.randint(0, len(questions)-1)]
    # END

    answers = MultipleChoiceAnswer.objects.filter(question=question)

    context = {
        'question': question,
        'answers': answers,
    }

    return render(request, 'quiz/multipleChoiceQuestion.html', context)


def trueFalseQuestion(request, question):

    # REMOVE LATER
    questions = TrueFalseQuestion.objects.all()
    question = questions[random.randint(0, len(questions) - 1)]
    # END

    answers = ('True', 'False')

    context = {
        'question': question,
        'answers': answers,
    }

    return render(request, 'quiz/trueFalseQuestion.html', context)


def textQuestion(request, question):

    ## REMOVE LATER
    questions = TextQuestion.objects.all()
    question = questions[random.randint(0, len(questions) - 1)]
    # END

    answers = question.answer

    context = {
        'question': question,
        'answer': answers,
    }

    return render(request, 'quiz/textQuestion.html', context)

def numberQuestion(request, question):

    ## REMOVE LATER
    questions = NumberQuestion.objects.all()
    question = questions[random.randint(0, len(questions) - 1)]
    # END

    answers = question.answer

    context = {
        'question': question,
        'answer': answers,
    }

    return render(request, 'quiz/numberQuestion.html', context)
