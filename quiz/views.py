from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Func, F
from django.shortcuts import render
from quiz.models import *
from quiz.forms import *
from django.contrib import messages


def question(request):
    """
    POST: updates player and question rating
    GET: gets next question to be answered and makes it so that "quiz" is rendered

    :param request: Request to be handled

    :return: JsonResponse, HttPResponse, render
    """
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
                questionReturn = PlayerAnswer.objects.filter(player=request.user.player).order_by('-answer_date')[len(questions)-1].question

            question = (list(TrueFalseQuestion.objects.filter(id=questionReturn.id))
                + list(MultipleChoiceQuestion.objects.filter(id=questionReturn.id))
                + list(TextQuestion.objects.filter(id=questionReturn.id))
                + list(NumberQuestion.objects.filter(id=questionReturn.id)))[0]

            # In order to have recently answered questions from current topics in list over reportable questions in report_modal
            # How far back the list of questions goes is defined by REPORTABLE_AMOUNT
            # Only list questions that have been ANSWERED, not REPORTED (report_skip must equal False)
            REPORTABLE_AMOUNT = 2
            recent_questions = [pa.question for pa in PlayerAnswer.objects.order_by('-answer_date') if (pa.question.topic in topics and not pa.report_skip)]
            q_list = [question]
            for q in recent_questions:
                if q in q_list:
                    pass
                else:
                    q_list.append(q)
            recent_questions = q_list[1:REPORTABLE_AMOUNT+1]
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
    """
    POST: updates a player's PlayerTopic objects
    GET: gets a player's PlayerTopic objects and renders "select topics" page

    :param request: Request to be handled

    :return: HttPResponse, render
    """
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

        # If user has no current subject, redirect to same page and display a message
        # This happens if user has no PlayerTopic objects, i.e. if the user has never chosen topics before (new user)
        # or if the user's PlayerTopic objects have somehow been deleted
        if subject == '':
            messages.warning(request, 'You must select a subject')
            return HttpResponseRedirect('/quiz/select-topics/')

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
        try:
            subject = topicsInPlayer.first().topic.subject
            allTopics = Topic.objects.all().filter(subject=subject)
        except AttributeError:
            subject=None
            allTopics = topics

        playerTopics = [playerTopic.topic for playerTopic in topicsInPlayer] if len(topicsInPlayer) != allTopics.count() else []

        context = {
            'subjects': subjects,
            'topics': showtopics,
            'subject': subject,
            'playerTopics': playerTopics,

        }

        return render(request, 'quiz/select_topic.html', context)


def multipleChoiceQuestion(request, question, context):
    """
    Renders a MC-question

    :param request: request to be handled
    :param question: question to be rendered
    :param context: context to be edited

    :return: render
    """
    answers = MultipleChoiceAnswer.objects.filter(question=question)

    context.update({
        'question': question,
        'answers': answers,
    })

    return render(request, 'quiz/multipleChoiceQuestion.html', context)


def trueFalseQuestion(request, question, context):
    """
    Renders a TF-question

    :param request: request to be handled
    :param question: question to be rendered
    :param context: context to be edited

    :return: render
    """
    answers = (('true', 'True'), ('false', 'False'))

    context.update({
        'question': question,
        'answers': answers,
    })

    return render(request, 'quiz/trueFalseQuestion.html', context)


def textQuestion(request, question, context):
    """
    Renders a text question

    :param request: request to be handled
    :param question: question to be rendered
    :param context: context to be edited

    :return: render
    """
    answers = question.answer

    context.update({
        'question': question,
        'answer': answers,
    })

    return render(request, 'quiz/textQuestion.html', context)


def numberQuestion(request, question, context):
    """
    Renders a number question

    :param request: request to be handled
    :param question: question to be rendered
    :param context: context to be edited

    :return: render
    """
    answers = question.answer

    context.update({
        'question': question,
        'answer': answers,
    })

    return render(request, 'quiz/numberQuestion.html', context)


def newQuestion(request):
    """
    Renders "new question" page if user is logged in

    :param request: Request to be handled

    :return: HttPResponse, render
    """
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
    """
    POST: creates new text or number question if form valid and redirects back to "new question" page
    Otherwise renders "new question" page

    :param request: Request to be handled

    :return: HttPResponse, render
    """
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
    """
    POST: creates new TF-question if form valid and redirects back to "new question" page
    Otherwise renders "new question" page

    :param request: Request to be handled

    :return: HttPResponse, render
    """
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
    """
    POST: creates new MC-question if form valid and redirects back to "new question" page
    Otherwise renders "new question" page

    :param request: Request to be handled

    :return: HttPResponse, render
    """
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
    """
    POST: creates new QuestionReport object if form valid. Also creates new PlayerAnswer object to avoid being asked the
    question again immediately.
    Redirects to "quiz" afterwards and in all other cases.

    :param request: Request to be handled

    :return: HttPResponse
    """
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            userDict = form.cleaned_data
            QuestionReport.objects.create(
                player=request.user.player,
                question=Question.objects.get(pk=userDict['question_id']),
                red_right=userDict['red_right'],
                green_wrong=userDict['green_wrong'],
                unclear=userDict['unclear'],
                off_topic=userDict['off_topic'],
                inappropriate=userDict['inappropriate'],
                other=userDict['other'],
                comment=userDict['comment'],
            )
            # Make a PA-object so that player doesn't get this question again immediately
            # (set report_skip to True to mark it as skipped because of a report)
            PlayerAnswer.objects.create(
                player=request.user.player,
                question=Question.objects.get(pk=userDict['question_id']),
                result=True,
                report_skip=True,
            )
    return HttpResponseRedirect('/quiz')

 
def viewReports(request):
    # Only site admins are allowed to see and handle reports
    user = request.user
    if user.is_superuser:
        reportesQuestionIDs = QuestionReport.objects.all().values_list('question_id', flat=True)
        questions = Question.objects.filter(id__in=reportesQuestionIDs)
        reports = []

        for question in questions:
            reports.append([question, QuestionReport.objects.filter(question_id=question.id).count()])

        reports.sort(key=lambda tup: tup[1], reverse=True)

        context = {
            'reports': reports,
        }

        return render(request, 'quiz/viewReports.html', context)

    return HttpResponseRedirect('/')


def handleReport(request, question_id):
    # Only site admins are allowed to see and handle reports
    user = request.user
    if user.is_superuser:
        context = {
            'question_id': question_id,
            'reports': QuestionReport.objects.filter(question_id=question_id),
        }

        return render(request, 'quiz/handleReport.html', context)

    return HttpResponseRedirect('/')


def deleteReport(request, question_id):

    # Only site admins are allowed to delete questions
    user = request.user
    if user.is_superuser:
        question = Question.objects.get(pk=question_id)
        question.delete()
        return HttpResponseRedirect('/quiz/viewreports')
    return HttpResponseRedirect('/')


def statsDefault(request):
    try:
        return HttpResponseRedirect('/quiz/stats/%r' % request.user.player.subject().id)
    except AttributeError:
        return HttpResponseRedirect('/quiz/stats/0')


def stats(request, subject_id):
    subjects = Subject.objects.all()
    try:
        subject = Subject.objects.get(pk=subject_id)
    except Subject.DoesNotExist:
        subject = None

    context = {
        'subjects': subjects,
        'subject': subject,
        'ratingList': request.user.player.ratingList(subject),
        'subjectAnswers': request.user.player.subjectAnswers(),
    }
    return render(request, 'quiz/stats.html', context)

