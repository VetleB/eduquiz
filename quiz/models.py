from django.db import models
from django.contrib.auth.admin import User
from django.utils import timezone
from re import match
from django.http import JsonResponse
from django.contrib.contenttypes.fields import GenericForeignKey


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
    skill_lvl = models.DecimalField(max_digits=3, decimal_places=3, default=0, verbose_name='Skill Lvl')
    user = models.ForeignKey(User)

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


class Question(models.Model):
    question_text = models.TextField(max_length=200, verbose_name='Question')
    creator = models.ForeignKey(Player)
    creation_date = models.DateTimeField(default=timezone.now, verbose_name='Date')
    difficulty = models.DecimalField(max_digits=3, decimal_places=3, verbose_name='Difficulty')
    topic = models.ForeignKey(Topic, null=True, blank=True)

    def __str__(self):
        return self.question_text



class TextQuestion(Question):
    answer = models.CharField(max_length=50, verbose_name='Answer')
    def __str__(self):
        return super().question_text

    #Antar at self.answer er numerisk med tre desimaler
    def validate(self, userAnswer):
        userAnswer = userAnswer.strip().casefold().replace(',', '.')

        # Fjerner ledende nuller
        while userAnswer[0] == '0' and len(userAnswer) > 1:
            userAnswer = userAnswer[1:]

        correctNumOfDecimals = len(self.answer.split('.')[1])

        # sjekker om det er '.' i strengen
        if '.' in userAnswer:
            userAnswer = userAnswer.split('.')

            # gjør om heltallsdelen til '0' hvis den er ingenting
            if userAnswer[0] == "":
                userAnswer[0] = '0'


            numOfDecimals = len(userAnswer[1])

            # legger på nuller til det er korrekt antall desimaler
            if numOfDecimals < correctNumOfDecimals:
                userAnswer[1] += ''.join(['0']*(correctNumOfDecimals-numOfDecimals))

            #Fjerner ekstra nuller fra desimaldelen
            if numOfDecimals > correctNumOfDecimals:
                extra = userAnswer[1][correctNumOfDecimals:]
                zeroMatch = match(r'^0*$', extra)
                if zeroMatch:
                    userAnswer[1] = userAnswer[1][0:correctNumOfDecimals]

            userAnswer = '.'.join(userAnswer)
        else:
            userAnswer += '.' + ''.join(['0']*correctNumOfDecimals)

        # matcher et heksadesimalt tall med desimaler
        patternMatch = bool(match(r'^0*[0-9a-f]*[.][0-9a-f]*$', userAnswer))
        return (userAnswer == self.answer.casefold()) and patternMatch

    def answerFeedback(self, answer):
        answeredCorrect = self.validate(answer)
        return {
            'answer': str(answer),
            'correct': str(self.answer),
            'answeredCorrect': answeredCorrect,
        }


class TrueFalseQuestion(Question):
    answer = models.BooleanField(verbose_name='Answer')

    def __str__(self):
        return super().question_text

    def answerFeedback(self, answer):
        answeredCorrect = answer == self.answer
        return {
            'answer': str(answer),
            'correct': str(self.answer),
            'answeredCorrect': answeredCorrect,
        }


class MultipleChoiceQuestion(Question):

    def __str__(self):
        return super().question_text

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
        return '%b - %s - %s' % (self.result, self.player, self.question)
