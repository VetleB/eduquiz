from django.db import models
from django.contrib.auth.admin import User
from django.utils import timezone
from re import match
from django.http import JsonResponse


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

    def rating(self):
        return PlayerRating.getRating(self)

    def update(self, question, win):
        win = int(win)
        QUESTION_K = 8
        PLAYER_K = 16
        RATING_CAP = 150

        rating = self.rating()

        if rating - question.rating < RATING_CAP:
            newrating = rating + PLAYER_K * (win - self.exp(rating, question.rating))
            question.rating += QUESTION_K * ((1-win) - self.exp(question.rating, rating))
            question.save()
            PlayerRating.setRating(self, newrating)

    def exp(self, a, b):
            return 1/(1+pow(10,(b-a)/400))

    def virtualRating(self, topics):
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


class Topic(models.Model):
    title = models.CharField(max_length=100, verbose_name='Title')
    subject = models.ForeignKey(Subject)

    def __str__(self):
        return self.title


class PlayerTopic(models.Model):
    player = models.ForeignKey(Player)
    topic = models.ForeignKey(Topic)


class PlayerRating(models.Model):
    player = models.ForeignKey(Player, blank=True)
    subject = models.ForeignKey(Subject, blank=True)
    rating = models.DecimalField(default=1200, max_digits=8, decimal_places=3, verbose_name='Rating')

    @staticmethod
    def getRatingObject(player, subject=None):
        if subject == None:
            try:
                subject = PlayerTopic.objects.filter(player=player).first().topic.subject
            except PlayerTopic.DoesNotExist:
                return None
        try:
            return PlayerRating.objects.get(player=player, subject=subject)
        except PlayerRating.DoesNotExist:
            return PlayerRating.objects.create(player=player, subject=subject)

    @staticmethod
    def getRating(player, subject=None):
        return PlayerRating.getRatingObject(player, subject).rating

    @staticmethod
    def setRating(player, rating, subject=None):
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
        userAnswer = inAnswer.strip().casefold()
        correctAnswer = self.answer.strip().casefold()

        # Fjerner alt som ikke er alfanumerisk
        userAnswer = ''.join([c for c in userAnswer if c.isalnum()])
        correctAnswer = ''.join([c for c in correctAnswer if c.isalnum()])

        return userAnswer == correctAnswer

    def answerFeedbackRaw(self, answer):
        return self.answerFeedback(answer)

    def answerFeedback(self, answer):
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
    report_skip = models.BooleanField(verbose_name='Report', default=False)


class PropAnswerdQuestionInSubject(Property):
    number = models.IntegerField(default=0, verbose_name="Number of answers")
    subject = models.ForeignKey(Subject, verbose_name="Subject")

    def isUnlocked(self, player):
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
