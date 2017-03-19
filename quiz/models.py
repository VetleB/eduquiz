from django.db import models
from django.contrib.auth.admin import User
from django.utils import timezone
from re import match
from django.http import JsonResponse


class Achievement(models.Model):
    name = models.CharField(max_length=50, verbose_name='Title')

    def __str__(self):
        return self.name


class Title(models.Model):
    title = models.CharField(max_length=50, verbose_name='Title')
    achievement = models.ForeignKey(Achievement, blank=True, null=True)

    def __str__(self):
        return self.title


class Player(models.Model):
    title = models.ForeignKey(Title, blank=True, null=True)
    rating = models.DecimalField(default=1200, max_digits=8, decimal_places=3, verbose_name='Rating')
    user = models.OneToOneField(User)

    def update(self, question, win):
            win = int(win)
            QUESTION_K = 8
            PLAYER_K = 16

            rating = self.rating + PLAYER_K * (win - self.exp(self.rating, question.rating))
            question.rating += QUESTION_K * ((1-win) - self.exp(question.rating, self.rating))
            question.save()
            self.rating = rating
            self.save()

    def exp(self, a, b):
            return 1/(1+pow(10,(b-a)/400))

    def __str__(self):
        return self.user.username


class AchievementUnlock(models.Model):
    player = models.ForeignKey(Player)
    achievement = models.ForeignKey(Achievement)
    date = models.DateTimeField(default=timezone.now, verbose_name='Date')

    def __str__(self):
        return '%s - %s' % (self.player, self.achievement)


class TitleUnlock(models.Model):
    player = models.ForeignKey(Player)
    title = models.ForeignKey(Title)

    def __str__(self):
        return '%s - %s' % (self.player, self.title)


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

    def __str__(self):
        return "%s - %s" % (self.player, self.topic)


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

    # Antar at self.answer er numerisk
    def validate(self, inAnswer):

        userAnswer = inAnswer.casefold().strip().replace(',', '.')
        correctAnswer = self.answer.casefold().strip().replace(',', '.')

        # Fjerner ledende nuller
        while len(userAnswer) > 1 and userAnswer[0] == '0':
            userAnswer = userAnswer[1:]

        # Gjør om heltallsdelen til '0' hvis den er ingenting
        if userAnswer[0] == '.':
            userAnswer = '0' + userAnswer

        if '.' not in correctAnswer:
            if '.' in userAnswer:
                spl = userAnswer.split('.')
                if match(r'^0*$', spl[1]):
                    return spl[0] == correctAnswer
                return False
            return userAnswer == correctAnswer

        correctNumOfDecimals = len(correctAnswer.split('.')[1])

        # Sjekker om det er '.' i strengen
        if '.' in userAnswer:
            userAnswer = userAnswer.split('.')
            numOfDecimals = len(userAnswer[1])

            # Legger på nuller til det er korrekt antall desimaler
            if numOfDecimals < correctNumOfDecimals:
                userAnswer[1] += ''.join(['0']*(correctNumOfDecimals-numOfDecimals))

            # Fjerner ekstra nuller fra desimaldelen
            if numOfDecimals > correctNumOfDecimals:
                extra = userAnswer[1][correctNumOfDecimals:]
                zeroMatch = match(r'^0*$', extra)
                if zeroMatch:
                    userAnswer[1] = userAnswer[1][0:correctNumOfDecimals]

            userAnswer = '.'.join(userAnswer)
        else:
            userAnswer += '.' + ''.join(['0']*correctNumOfDecimals)

        # Matcher et heksadesimalt tall med desimaler
        patternMatch = bool(match(r'^0*[0-9a-f]*[.][0-9a-f]*$', userAnswer))
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

    def __str__(self):
        return '%r - %s - %s' % (self.result, self.player, self.question)


class QuestionReport(models.Model):
    player = models.ForeignKey(Player)
    question = models.ForeignKey(Question)
    red_right = models.BooleanField(verbose_name='Red answer right')
    green_wrong = models.BooleanField(verbose_name='Green answer wrong')
    ambiguous = models.BooleanField(verbose_name='Ambiguous')
    other = models.BooleanField(verbose_name='Other')
    comment = models.CharField(max_length=400, verbose_name='Comment')
