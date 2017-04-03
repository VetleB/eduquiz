from django.db import models
from django.contrib.auth.admin import User
from django.utils import timezone
from re import match
from django.db.models import Count
from datetime import datetime


class Achievement(models.Model):
    name = models.CharField(max_length=50, verbose_name='Title', default='')
    badge = models.ImageField(verbose_name='Badge', blank=True, null=True)

    def isAchieved(self, player):
        for prop in self.property_set.all():
            try:
                PropertyUnlock.objects.get(player=player, prop=prop)
            except PropertyUnlock.DoesNotExist:
                return False
        return True

    def update(self, player):
        if self.isAchieved(player):
            try:
                AchievementUnlock.objects.get(player=player, achievement=self)
            except AchievementUnlock.DoesNotExist:
                AchievementUnlock(player=player, achievement=self).save()
                titles = Title.objects.filter(achievement=self)
                for title in titles:
                    TitleUnlock(title=title, player=player).save()

    def __str__(self):
        return self.name


class Property(models.Model):
    name = models.CharField(max_length=50, verbose_name='Name', default='')
    achievements = models.ManyToManyField(Achievement, blank=True)

    # return wether the propery is unlocked or not
    # implemented in subclasses
    def isUnlocked(self, player):
        return True

    def update(self, player):
        if self.isUnlocked(player):
            try:
                PropertyUnlock.objects.get(player=player, prop=self)
            except PropertyUnlock.DoesNotExist:
                PropertyUnlock(player=player, prop=self).save()
            for achievement in self.achievements.all():
                achievement.update(player)
        else:
            try:
                PropertyUnlock.objects.get(player=player, prop=self).delete()
            except PropertyUnlock.DoesNotExist:
                pass

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'properties'


class Trigger(models.Model):
    name = models.CharField(max_length=50, verbose_name='Name')
    properties = models.ManyToManyField(Property, blank=True)

    def trigger(self, player):
        for prop in self.properties.all():
            prop.update(player)

    def __str__(self):
        return self.name


class Title(models.Model):
    title = models.CharField(max_length=50, verbose_name='Title')
    achievement = models.ForeignKey(Achievement, blank=True, null=True)

    def __str__(self):
        return self.title


class Player(models.Model):
    title = models.ForeignKey(Title, blank=True, null=True)
    user = models.OneToOneField(User)

    def setRating(self, rating):
        PlayerRating.setRating(self, rating)

    def subjectAnswers(self):
        counts = []
        titles = []

        query = PlayerAnswer.objects.filter(player=self).values('question__topic__subject').annotate(count=Count('question__topic__subject'))
        for element in query:
            sub = Subject.objects.get(pk=element['question__topic__subject'])
            count = element['count']
            counts.append(count)
            titles.append(sub.title)

        return (counts, titles)

    def ratingList(self, subject=None):
        if subject == None:
            subject = self.subject()
        qset = PlayerAnswer.objects.filter(player=self, question__topic__subject=subject).values_list('rating', 'answer_date').order_by('answer_date')
        return ([float(a[0]) for a in qset], [datetime.strftime(a[1], '%d %B') for a in qset])

    #def ratingLists(self):
    #    li = []
    #    for subject in Subject.objects.all():
    #        li2 = 50 * [1200]
    #        qset = PlayerAnswer.objects.filter(player=self, question__topic__subject=subject).values_list('rating', flat=True)
    #        li2[50-len(qset):] = [int(rating) for rating in qset]
    #        li.append((li2, subject.title))
    #    return (range(1, 51), li)

    def subject(self):
        try:
            return PlayerTopic.objects.filter(player=self).first().topic.subject
        except AttributeError:
            return None

    def rating(self):
        return PlayerRating.getRating(self)

    def update(self, question, win):
        """
        Adjust rating of player and question when question has been answered

        :param question: question that has been answered
        :type question: Question object

        :param win: True if question was answered correctly, False otherwise
        :type win: boolean

        :return: None
        :rtype: None
        """
        win = int(win)
        QUESTION_K = 8
        PLAYER_K = 16
        RATING_CAP = 150

        rating = float(self.rating())
        questionRating = float(question.rating)

        if rating - questionRating < RATING_CAP:
            newrating = rating + PLAYER_K * (win - self.exp(rating, questionRating))
            question.rating = questionRating + QUESTION_K * ((1-win) - self.exp(questionRating, rating))
            question.save()
            PlayerRating.setRating(self, newrating)

        PlayerAnswer.objects.create(player=self, question=question, result=win)

    def exp(self, a, b):
        """
        Returns a fraction to be used in adjustment of rating.
        The larger the difference between opponents, the smaller the return value will be,
        and a lesser impact will be made on the ratings.

        :param a: Rating of the one being adjusted
        :type a: float

        :param b: Opponent's rating
        :type b: float

        :return: Fraction
        :rtype: float
        """
        return 1/(1+pow(10, (b-a)/400))

    def virtualRating(self, topics):
        """
        Return rating adjusted up if player is on win streak, down if on loss streak.

        :param topics: List of PlayerTopic objects
        :type topics: list

        :return: Player's adjusted rating
        :rtype: float
        """
        VIRTUAL_K = 10
        VIRTUAL_C = 5

        # Get the VIRTUAL_C latest answers that are not reports (report_skip must equal False) and in/decrease rating thereafter
        answers = [pa for pa in PlayerAnswer.objects.filter(player=self, question__topic__in=topics).order_by('-answer_date') if pa.report_skip!=True][:VIRTUAL_C]
        virtual = sum([VIRTUAL_K if answer.result else -VIRTUAL_K for answer in answers])
        return PlayerRating.getRating(self) + virtual

    def __str__(self):
        return self.user.username


class PropertyUnlock(models.Model):
    player = models.ForeignKey(Player)
    prop = models.ForeignKey(Property)


class AchievementUnlock(models.Model):
    player = models.ForeignKey(Player)
    achievement = models.ForeignKey(Achievement)
    date = models.DateTimeField(default=timezone.now, verbose_name='Date')


class TitleUnlock(models.Model):
    player = models.ForeignKey(Player)
    title = models.ForeignKey(Title)


class Category(models.Model):
    title = models.CharField(max_length=100, verbose_name='Title')

    def __str__(self):
        return self.title


class Subject(models.Model):
    title = models.CharField(max_length=100, verbose_name='Title')
    short = models.CharField(max_length=10, verbose_name='Short')
    code = models.CharField(max_length=10, verbose_name='Code')
    category = models.ForeignKey(Category)

    def __str__(self):
        return '%s - %s' % (self.code, self.title)

    def highscore(self):
        query = PlayerRating.objects.filter(subject=self).values_list('player', 'rating').order_by('-rating')
        return [(a[0]+1, Player.objects.get(pk=a[1][0]).user.username, int(a[1][1])) for a in enumerate(query)]


class Topic(models.Model):
    title = models.CharField(max_length=100, verbose_name='Title')
    subject = models.ForeignKey(Subject)

    def __str__(self):
        return self.title


class PlayerTopic(models.Model):
    player = models.ForeignKey(Player)
    topic = models.ForeignKey(Topic)


class PlayerRating(models.Model):
    player = models.ForeignKey(Player)
    subject = models.ForeignKey(Subject)
    rating = models.DecimalField(default=1200, max_digits=8, decimal_places=3, verbose_name='Rating')

    @staticmethod
    def getRatingObject(player, subject=None):
        if subject == None:
            subject = player.subject()
        if not subject:
            return None
        try:
            return PlayerRating.objects.get(player=player, subject=subject)
        except PlayerRating.DoesNotExist:
            return PlayerRating.objects.create(player=player, subject=subject)

    @staticmethod
    def getRating(player, subject=None):
        """
        Get rating of a player in a subject

        :param player: player for whom rating is wanted
        :type player: Player object

        :param subject: subject for which player's rating is wanted
        :type subject: Subject object

        :return: Player's rating in subject
        :rtype: float
        """
        playerRating = PlayerRating.getRatingObject(player, subject)
        if playerRating:
            return playerRating.rating
        else:
            return 1200

    @staticmethod
    def setRating(player, rating, subject=None):
        """
        Set a player's rating in a subject

        :param player: Player who's rating is to be changed
        :type player: Player object

        :param rating: Rating the player is to get
        :type rating: float

        :param subject: Subject in which a player's rating is to be changed
        :type subject: Subject object

        :return: None
        :rtype: None
        """
        playerRating = PlayerRating.getRatingObject(player, subject)
        playerRating.rating = rating
        playerRating.save()


class Question(models.Model):
    question_text = models.TextField(max_length=200, verbose_name='Question')
    creator = models.ForeignKey(Player, blank=True, null=True)
    creation_date = models.DateTimeField(default=timezone.now, verbose_name='Date')
    rating = models.DecimalField(default=1200, max_digits=8, decimal_places=3, verbose_name='Rating')
    topic = models.ForeignKey(Topic, null=True, blank=True)

    def __str__(self):
        return self.question_text


class TextQuestion(Question):
    answer = models.CharField(max_length=50, verbose_name='Answer')

    def validate(self, inAnswer):
        """
        Determines whether a text answer is right or wrong

        :param inAnswer: Answer to be validated
        :type inAnswer: string

        :return: Whether answer is right or not
        :rtype: boolean
        """
        userAnswer = inAnswer.strip().casefold()
        correctAnswer = self.answer.strip().casefold()

        # Fjerner alt som ikke er alfanumerisk
        userAnswer = ''.join([c for c in userAnswer if c.isalnum()])
        correctAnswer = ''.join([c for c in correctAnswer if c.isalnum()])

        return userAnswer == correctAnswer

    def answerFeedbackRaw(self, answer):
        return self.answerFeedback(answer)

    def answerFeedback(self, answer):
        """
        Validates answer and returns feedback as JSON-object

        :param answer: Answer to be validated
        :type answer: string

        :return: JSON-object
        :rtype: dict
        """
        answeredCorrect = self.validate(answer)
        return {
            'answer': answer,
            'correct': self.answer,
            'answeredCorrect': answeredCorrect,
        }


class NumberQuestion(Question):
    answer = models.CharField(max_length=50, verbose_name='Answer')
    def __str__(self):
        return super().question_text

    def validate(self, inAnswer):
        """
        Determines whether a number answer is right or wrong

        :param inAnswer: Answer to be validated
        :type inAnswer: string

        :return: Whether answer is right or not
        :rtype: boolean
        """
        if inAnswer == '':
            return False

        userAnswer = inAnswer.casefold().strip().replace(',', '.')
        correctAnswer = self.answer.casefold().strip().replace(',', '.')

        # Removes leading zeros
        while len(userAnswer) > 1 and userAnswer[0] == '0':
            userAnswer = userAnswer[1:]

        # If no integer part, set it to '0'
        if userAnswer[0] == '.':
            userAnswer = '0' + userAnswer

        # If answer not a decimal, check if user's answer only has zeros in the decimal part and compare
        if '.' not in correctAnswer:
            if '.' in userAnswer:
                spl = userAnswer.split('.')
                if match(r'^0*$', spl[1]):
                    return spl[0] == correctAnswer
                return False
            return userAnswer == correctAnswer

        correctNumOfDecimals = len(correctAnswer.split('.')[1])

        if '.' in userAnswer:
            userAnswer = userAnswer.split('.')
            numOfDecimals = len(userAnswer[1])

            # Adds zeros to decimal part to get correct length
            if numOfDecimals < correctNumOfDecimals:
                userAnswer[1] += ''.join(['0']*(correctNumOfDecimals-numOfDecimals))

            # Remove trailing zeros to get correct length
            if numOfDecimals > correctNumOfDecimals:
                extra = userAnswer[1][correctNumOfDecimals:]
                zeroMatch = match(r'^0*$', extra)
                if zeroMatch:
                    userAnswer[1] = userAnswer[1][0:correctNumOfDecimals]

            userAnswer = '.'.join(userAnswer)
        else:
            userAnswer += '.' + ''.join(['0']*correctNumOfDecimals)

        # Make sure user's answer is on right format
        patternMatch = bool(match(r'^0*[0-9a-f]*[.][0-9a-f]*$', userAnswer))
        # Compare user's answer with the actual answer
        return (userAnswer == correctAnswer) and patternMatch

    def answerFeedbackRaw(self, answer):
        return self.answerFeedback(answer)

    def answerFeedback(self, answer):
        """
        Validates answer and returns feedback as JSON-object

        :param answer: Answer to be validated
        :type answer: string

        :return: JSON-object
        :rtype: dict
        """
        answeredCorrect = self.validate(answer)
        return {
            'answer': answer,
            'correct': self.answer,
            'answeredCorrect': answeredCorrect,
        }


class TrueFalseQuestion(Question):
    answer = models.BooleanField(verbose_name='Answer')

    def __str__(self):
        return super().question_text

    def answerFeedbackRaw(self, answer):
        return self.answerFeedback(answer.capitalize() == 'True')

    def answerFeedback(self, answer):
        """
        Validates answer and returns feedback as JSON-object

        :param answer: Answer to be validated
        :type answer: boolean

        :return: JSON-object
        :rtype: dict
        """
        answeredCorrect = answer == self.answer
        return {
            'answer': answer,
            'correct': self.answer,
            'answeredCorrect': answeredCorrect,
        }


class MultipleChoiceQuestion(Question):

    def __str__(self):
        return super().question_text

    def answerFeedbackRaw(self, answer):
        try:
            return self.answerFeedback(int(answer))
        except ValueError:
            return self.answerFeedback(1)

    def answerFeedback(self, answerID):
        """
        Validates answer and returns feedback as JSON-object

        :param answer: Answer to be validated
        :type answer: int

        :return: JSON-object
        :rtype: dict
        """
        answer = MultipleChoiceAnswer.objects.get(id=answerID)
        answeredCorrect = answer.correct
        answers = MultipleChoiceAnswer.objects.filter(question=self.id, correct=True)
        answerIDs = [answer.id for answer in answers]
        return {
            'answer': answerID,
            'correct': answerIDs,
            'answeredCorrect': answeredCorrect,
        }


class MultipleChoiceAnswer(models.Model):
    question = models.ForeignKey(MultipleChoiceQuestion)
    answer = models.CharField(max_length=100, verbose_name='Answer')
    correct = models.BooleanField(verbose_name='Correct')

    def __str__(self):
        return self.answer


class PlayerAnswer(models.Model):
    player = models.ForeignKey(Player)
    question = models.ForeignKey(Question)
    result = models.BooleanField(verbose_name='Result')
    answer_date = models.DateTimeField(default=timezone.now, verbose_name='Date')
    rating = models.DecimalField(max_digits=8, decimal_places=3, verbose_name='Rating')
    report_skip = models.BooleanField(verbose_name='Report', default=False)

    def save(self, *args, **kwargs):
        """
        Saves PlayerAnswer after setting rating to player's rating
        Model.save doc: https://docs.djangoproject.com/en/1.10/_modules/django/db/models/base/#Model.save

        :param args: see Model.save documentation
        :param kwargs: see Model.save documentation

        :return: None
        :rtype: None
        """
        self.rating = self.player.rating()
        super(PlayerAnswer, self).save(*args, **kwargs)



class PropAnswerdQuestionInSubject(Property):
    number = models.IntegerField(default=0, verbose_name="Number of answers")
    subject = models.ForeignKey(Subject, verbose_name="Subject")

    def isUnlocked(self, player):
        """ Return whether property is unlocked """
        return len(PlayerAnswer.objects.filter(player=player, question__topic__subject=self.subject)) >= self.number

    def __str__(self):
        return '%r in %s' % (self.number, self.subject.title)


class QuestionReport(models.Model):
    player = models.ForeignKey(Player)
    question = models.ForeignKey(Question)
    red_right = models.BooleanField(verbose_name='Red answer right', default=False)
    green_wrong = models.BooleanField(verbose_name='Green answer wrong', default=False)
    unclear = models.BooleanField(verbose_name='Ambiguous', default=False)
    off_topic = models.BooleanField(verbose_name='Off-topic', default=False)
    inappropriate = models.BooleanField(verbose_name="inappropriate", default=False)
    other = models.BooleanField(verbose_name='Other', default=False)
    comment = models.CharField(max_length=500, verbose_name='Comment', default="")
