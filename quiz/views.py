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

            topics = [PT.topic for PT in list(PlayerTopic.objects.filter(player=request.user.player))]

            if not topics:
                return HttpResponseRedirect('/quiz/select-topics')

            virtualRating = request.user.player.virtualRating(topics)
            questions = Question.objects.filter(topic__in=topics).annotate(dist=Func(F('rating') - virtualRating, function='ABS')).order_by('dist')

            REPEAT = 5

            questionReturn = None

            for question in questions:
                if question not in [pa.question for pa in list(PlayerAnswer.objects.filter(player=request.user.player).order_by('-answer_date')[:REPEAT])]:
                    questionReturn = question
                    break

            if not questionReturn:
                question = PlayerAnswer.objects.filter(player=request.user.player).order_by('-answer_date')[len(questions)-1].question

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

            return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/')


def selectTopic(request):

    if request.method == 'POST':
        # deletes all previously selected topics
        PlayerTopic.objects.filter(player=request.user.player).delete()

        try:
            # string
            subject = request.POST['subject']
            # string of topics separated by comma
            topics = request.POST['topics']
        except ValueError:
            return HttpResponseRedirect('/')

        # list of strings
        topics = topics.split(',')

        # if no specified topics, include all topics that belong to subject
        if topics[0] == '':
            topics = [topic.title for topic in Topic.objects.filter(subject=Subject.objects.get(title=subject))]

        # make new player-topic-links in database
        for topic in topics:
            try:
                PlayerTopic.objects.create(
                    player = request.user.player,
                    topic = Topic.objects.get(title=topic),
                )
            except Topic.DoesNotExist:
                pass

        return HttpResponseRedirect('/quiz')
    else:
        subjects = Subject.objects.all()
        topics = Topic.objects.all()

        context = {
            'subjects': subjects,
            'topics': topics,
        }

        return render(request, 'quiz/select_topic.html', context)

def multipleChoiceQuestion(request, question):

    answers = MultipleChoiceAnswer.objects.filter(question=question)

    context = {
        'question': question,
        'answers': answers,
    }

    return render(request, 'quiz/multipleChoiceQuestion.html', context)


def trueFalseQuestion(request, question):

    answers = (('true', 'True'), ('false', 'False'))

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


def newQuestion(request):

    context = {

    }

    return render(request, 'quiz/newQuestion.html', context)
