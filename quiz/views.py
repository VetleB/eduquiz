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

            # In order to have recently answered questions from current topics in list over reportable questions in report_modal
            # How far back the list of questions goes is defined by REPORTABLE_AMOUNT
            # Only list questions that have been ANSWERED, not REPORTED (report_skip must equal False)
            REPORTABLE_AMOUNT = 2
            recent_questions = [pa.question for pa in PlayerAnswer.objects.order_by('-answer_date') if (pa.question.topic in topics and not pa.report_skip)]
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

        showtopics = []
        for topic in topics:
            if topic.question_set.count() > 0:
                showtopics.append(topic)



        topicsInPlayer = PlayerTopic.objects.filter(player=request.user.player)
        playerTopics= [playerTopic.topic for playerTopic in topicsInPlayer]

        try:
            subject = topicsInPlayer.first().topic.subject
        except AttributeError:
            subject=None


        context = {
            'subjects': subjects,
            'topics': showtopics,
            'subject': subject,
            'playerTopics': playerTopics,

        }

        return render(request, 'quiz/select_topic.html', context)

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
    if request.user.is_authenticated:
        subjects = Subject.objects.all()
        topics = Topic.objects.all()

        context = {
            'subjects': subjects,
            'topics': topics,
        }

        return render(request, 'quiz/newQuestion.html', context)
    return HttpResponseRedirect('/')


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

            if form.cleaned_data['text'] == 'True':
                question = TextQuestion(
                    question_text = form.cleaned_data['question'],
                    creator = creator,
                    rating = 800 + 100 * int(form.cleaned_data['rating']),
                    topic = topic,
                    answer = form.cleaned_data['answer'],
                )
            elif form.cleaned_data['text'] == 'False':
                question = NumberQuestion(
                    question_text = form.cleaned_data['question'],
                    creator = creator,
                    rating = 800 + 100 * int(form.cleaned_data['rating']),
                    topic = topic,
                    answer = form.cleaned_data['answer'],
                )
            question.save()
            messages.success(request, 'Question successfully created')
            return HttpResponseRedirect('/quiz/new/')
    else:
        form = TextQuestionForm()

    subjects = Subject.objects.all()
    topics = Topic.objects.all()

    context = {
        'tForm': form,
        'subjects': subjects,
        'topics': topics,
        'active': 'text',
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
                rating = 800 + 100 * int(form.cleaned_data['rating']),
                topic = topic,
                answer = form.cleaned_data['correct'] == 'True',
            )
            question.save()
            messages.success(request, 'Question successfully created')
            return HttpResponseRedirect('/quiz/new/')
    else:
        form = TrueFalseQuestionForm()

    subjects = Subject.objects.all()
    topics = Topic.objects.all()

    context = {
        'tfForm': form,
        'subjects': subjects,
        'topics': topics,
        'active': 'truefalse',
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
                rating = 800 + 100 * int(form.cleaned_data['rating']),
                topic = topic,
            )
            question.save()

            alternative1 = MultipleChoiceAnswer(
                question = question,
                answer = form.cleaned_data['answer1'],
                correct = form.cleaned_data['correct'] == 'Alt1',
            )

            alternative2 = MultipleChoiceAnswer(
                question = question,
                answer = form.cleaned_data['answer2'],
                correct = form.cleaned_data['correct'] == 'Alt2',
            )

            alternative3 = MultipleChoiceAnswer(
                question = question,
                answer = form.cleaned_data['answer3'],
                correct = form.cleaned_data['correct'] == 'Alt3',
            )

            alternative4 = MultipleChoiceAnswer(
                question = question,
                answer = form.cleaned_data['answer4'],
                correct = form.cleaned_data['correct'] == 'Alt4',
            )

            alternative1.save()
            alternative2.save()
            alternative3.save()
            alternative4.save()
            messages.success(request, 'Question successfully created')
            return HttpResponseRedirect('/quiz/new/')
    else:
        form = MultipleChoiceQuestionForm()

    subjects = Subject.objects.all()
    topics = Topic.objects.all()

    context = {
        'mcForm': form,
        'subjects': subjects,
        'topics': topics,
        'active': 'multiplechoice',
    }

    return render(request, 'quiz/newQuestion.html', context)

def report(request):
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
            # Make a PA-object so that player doesn't get this question again immediatly (set report_skip to True to mark it as skipped because of a report)
            PlayerAnswer.objects.create(
                player=request.user.player,
                question=Question.objects.get(question_text=userDict['question_text']),
                result=True,
                report_skip=True,
            )
    return HttpResponseRedirect('/quiz')
