from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Func, F
from django.shortcuts import render
from quiz.models import *
import random


def question(request):
    if request.method == 'POST':
        try:
            questionID = int(request.POST['question'])
        except ValueError:
            JsonResponse({}, safe=False)

        questionList = (list(TrueFalseQuestion.objects.filter(id=questionID))
            + list(MultipleChoiceQuestion.objects.filter(id=questionID))
            + list(TextQuestion.objects.filter(id=questionID))
            + list(NumberQuestion.objects.filter(id=questionID)))

        if questionList:
            question = questionList[0]
        else:
            JsonResponse({}, safe=False)

        feedback = question.answerFeedbackRaw(request.POST['answer'])

        if hasattr(request, 'user') and hasattr(request.user, 'player') and feedback:
            result = feedback['answeredCorrect']
            PlayerAnswer(player=request.user.player, question=question, result=result).save()
            request.user.player.update(question, result)

        return JsonResponse(feedback, safe=False)

    else:
        if hasattr(request, 'user') and hasattr(request.user, 'player'):

            playerTopics = [PT.topic for PT in list(PlayerTopic.objects.filter(player=request.user.player))]

            # Hvis player ikke har spesifisert topics, ta et tilfeldig spørsmål. Må endres senere når alle brukere alltid har en mengde topics/et subject
            if not playerTopics:
                question = Question.objects.annotate(dist=Func(F('rating') - request.user.player.rating, function='ABS')).order_by('dist').first()
            else:
                question = Question.objects.filter(topic__in=playerTopics).annotate(dist=Func(F('rating') - request.user.player.rating, function='ABS')).order_by('dist').first()

            question = (list(TrueFalseQuestion.objects.filter(id=question.id))
                + list(MultipleChoiceQuestion.objects.filter(id=question.id))
                + list(TextQuestion.objects.filter(id=question.id))
                + list(NumberQuestion.objects.filter(id=question.id)))[0]

            if isinstance(question, MultipleChoiceQuestion):
                return multipleChoiceQuestion(request, question)

            elif isinstance(question, TrueFalseQuestion):
                return trueFalseQuestion(request, question)

            elif isinstance(question, TextQuestion):
                return textQuestion(request, question)

            elif isinstance(question, NumberQuestion):
                return numberQuestion(request, question)

            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/')


def playerTopic(request):

    PlayerTopic.objects.filter(player=request.user.player).delete()

    try:
        #string
        subject = request.POST['subject']
        #string of topics separated by comma
        topics = request.POST['topics']
    except ValueError:
        return HttpResponseRedirect('/')

    # list of strings
    topics = topics.split(',')

    for ts in topics:
        PlayerTopic.objects.create(
            player = request.user.player,
            topic = Topic.objects.filter(title=ts),
        )
    return HttpResponseRedirect('/quiz')


def multipleChoiceQuestion(request, question):

    answers = MultipleChoiceAnswer.objects.filter(question=question)

    context = {
        'question': question,
        'answers': answers,
    }

    return render(request, 'quiz/multipleChoiceQuestion.html', context)


def trueFalseQuestion(request, question):

    answers = ('True', 'False')

    context = {
        'question': question,
        'answers': answers,
    }

    return render(request, 'quiz/trueFalseQuestion.html', context)


def textQuestion(request, question):

    answers = question.answer

    context = {
        'question': question,
        'answer': answers,
    }

    return render(request, 'quiz/textQuestion.html', context)


def numberQuestion(request, question):

    answers = question.answer

    context = {
        'question': question,
        'answer': answers,
    }

    return render(request, 'quiz/numberQuestion.html', context)


def newMultiplechoice(request):

    context = {

    }

    return render(request, 'quiz/newMultiplechoice.html', context)


def newTrueorfalse(request):

    context = {

    }

    return render(request, 'quiz/newTrueorfalse.html', context)


def newTextanswer(request):

    context = {

    }

    return render(request, 'quiz/newTextanswer.html', context)

def newNumberanswer(request):

    context = {

    }

    return render(request, 'quiz/newNumberanswer.html', context)
