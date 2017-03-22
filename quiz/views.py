from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Func, F
from django.shortcuts import render
from quiz.models import *
from quiz.forms import *
import random
from django.contrib import messages

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

            # if no specified topics, grab random question. Change later when all player have topics
            if not playerTopics:
                return HttpResponseRedirect('/quiz/select-topics')
            else:
                question = Question.objects.filter(topic__in=playerTopics).annotate(dist=Func(F('rating') - request.user.player.rating, function='ABS')).order_by('dist').first()

            question = (list(TrueFalseQuestion.objects.filter(id=question.id))
                + list(MultipleChoiceQuestion.objects.filter(id=question.id))
                + list(TextQuestion.objects.filter(id=question.id))
                + list(NumberQuestion.objects.filter(id=question.id)))[0]

            # In order to have recently answered questions from current topics in list over reportable questions in report_modal
            # How far back the list goes is defined by REPORTABLE_AMOUNT
            REPORTABLE_AMOUNT = 2
            recent_questions = [PlAns.question for PlAns in PlayerAnswer.objects.order_by('-answer_date') if PlAns.question.topic in playerTopics]
            text_list = [question.question_text]
            return_list = []
            for q in recent_questions:
                if q.question_text in text_list:
                    pass
                else:
                    text_list.append(q.question_text)
                    return_list.append(q)
            recent_questions = return_list[0:REPORTABLE_AMOUNT]
            context = {
                'recent_questions': recent_questions,
            }

            if isinstance(question, MultipleChoiceQuestion):
                return multipleChoiceQuestion(request, question, context)

            elif isinstance(question, TrueFalseQuestion):
                return trueFalseQuestion(request, question, context)

            elif isinstance(question, TextQuestion):
                return textQuestion(request, question, context)

            elif isinstance(question, NumberQuestion):
                return numberQuestion(request, question, context)

            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/')


def selectTopic(request):

    subjects = Subject.objects.all()
    topics = Topic.objects.all()

    context = {
        'subjects': subjects,
        'topics': topics,
    }

    return render(request, 'quiz/select_topic.html', context)


def playerTopic(request):

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
        topics = [T.title for T in Topic.objects.filter(subject=Subject.objects.get(title=subject))]

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


def multipleChoiceQuestion(request, question, context):

    answers = MultipleChoiceAnswer.objects.filter(question=question)

    context.update({
        'question': question,
        'answers': answers,
    })

    return render(request, 'quiz/multipleChoiceQuestion.html', context)


def trueFalseQuestion(request, question, context):

    answers = (('true', 'True'), ('false', 'False'))

    context.update({
        'question': question,
        'answers': answers,
    })

    return render(request, 'quiz/trueFalseQuestion.html', context)


def textQuestion(request, question, context):

    answers = question.answer

    context.update({
        'question': question,
        'answer': answers,
    })

    return render(request, 'quiz/textQuestion.html', context)


def numberQuestion(request, question, context):

    answers = question.answer

    context.update({
        'question': question,
        'answer': answers,
    })

    return render(request, 'quiz/numberQuestion.html', context)


def newQuestion(request):

    subjects = Subject.objects.all()
    topics = Topic.objects.all()

    context = {
        'subjects': subjects,
        'topics': topics,
    }

    return render(request, 'quiz/newQuestion.html', context)


def newTextQuestion(request):
    if request.method == 'POST':
        form = TextQuestionForm(request.POST)
        if form.is_valid():
            if hasattr(request, 'user') and hasattr(request.user, 'player'):
                creator = request.user.player
            else:
                creator = None

            subject = Subject.objects.get(title=form.cleaned_data['subject'])
            topic = Topic.objects.get(subject=subject, title=form.cleaned_data['topics'])

            if form.cleaned_data['text']:
                question = TextQuestion(
                    question_text = form.cleaned_data['question'],
                    creator = creator,
                    rating = 700 + 100 * int(form.cleaned_data['rating']),
                    topic = topic,
                    answer = form.cleaned_data['answer'],
                )
            else:
                question = NumberQuestion(
                    question_text = form.cleaned_data['question'],
                    creator = creator,
                    rating = 700 + 100 * int(form.cleaned_data['rating']),
                    topic = topic,
                    answer = form.cleaned_data['answer'],
                )
            question.save()
            messages.success(request, 'Question successfully created')
    else:
        form = TextQuestionForm()

    subjects = Subject.objects.all()
    topics = Topic.objects.all()

    context = {
        'tForm': form,
        'subjects': subjects,
        'topics': topics,
    }

    return render(request, 'quiz/newQuestion.html', context)


def newTrueFalseQuestion(request):
    if request.method == 'POST':
        form = TrueFalseQuestionForm(request.POST)
        if form.is_valid():
            if hasattr(request, 'user') and hasattr(request.user, 'player'):
                creator = request.user.player
            else:
                creator = None

            subject = Subject.objects.get(title=form.cleaned_data['subject'])
            topic = Topic.objects.get(subject=subject, title=form.cleaned_data['topics'])

            question = TrueFalseQuestion(
                question_text = form.cleaned_data['question'],
                creator = creator,
                rating = 700 + 100 * int(form.cleaned_data['rating']),
                topic = topic,
                answer = bool(form.cleaned_data['correct']),
            )
            question.save()
            messages.success(request, 'Question successfully created')
    else:
        form = TrueFalseQuestionForm()

    subjects = Subject.objects.all()
    topics = Topic.objects.all()

    context = {
        'tfForm': form,
        'subjects': subjects,
        'topics': topics,
    }

    return render(request, 'quiz/newQuestion.html', context)


def newMultiplechoiceQuestion(request):
    if request.method == 'POST':
        form = MultipleChoiceQuestionForm(request.POST)

        if form.is_valid():
            if hasattr(request, 'user') and hasattr(request.user, 'player'):
                creator = request.user.player
            else:
                creator = None

            subject = Subject.objects.get(title=form.cleaned_data['subject'])
            topic = Topic.objects.get(subject=subject, title=form.cleaned_data['topics'])

            question = MultipleChoiceQuestion(
                question_text = form.cleaned_data['question'],
                creator = creator,
                rating = 700 + 100 * int(form.cleaned_data['rating']),
                topic = topic,
            )
            question.save()

            alternative1 = MultipleChoiceAnswer(
                question = question,
                answer = form.cleaned_data['answer1'],
                correct = bool(form.cleaned_data['correct1']),
            )

            alternative2 = MultipleChoiceAnswer(
                question = question,
                answer = form.cleaned_data['answer2'],
                correct = bool(form.cleaned_data['correct2']),
            )

            alternative3 = MultipleChoiceAnswer(
                question = question,
                answer = form.cleaned_data['answer2'],
                correct = bool(form.cleaned_data['correct2']),
            )

            alternative4 = MultipleChoiceAnswer(
                question = question,
                answer = form.cleaned_data['answer2'],
                correct = bool(form.cleaned_data['correct2']),
            )

            alternative1.save()
            alternative2.save()
            alternative3.save()
            alternative4.save()
            messages.success(request, 'Question successfully created')
    else:
        form = MultipleChoiceQuestionForm()

    subjects = Subject.objects.all()
    topics = Topic.objects.all()

    context = {
        'mcForm': form,
        'subjects': subjects,
        'topics': topics,
    }

    return render(request, 'quiz/newQuestion.html', context)


def report(request):
    # TODO: implement rest of report types
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            userDict = form.cleaned_data
            QuestionReport.objects.create(
                player = request.user.player,
                question = Question.objects.get(question_text=userDict['question_text']),
                red_right = userDict['red_right'],
                green_wrong = userDict['green_wrong'],
                unclear = userDict['unclear'],
                off_topic = userDict['off_topic'],
                inappropriate = userDict['inappropriate'],
                other = userDict['other'],
                comment = userDict['comment'],
            )
    return HttpResponseRedirect('/quiz')
