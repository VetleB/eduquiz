from django.db import models
from django.contrib.auth.admin import User


class Question(models.Model):
    question_text = models.TextField()
    creator = models.ForeignKey(User)
    difficulty = models.DecimalField(max_digits=3, decimal_places=3)

    class Meta:
        abstract = True


class TextAnswer(Question):
    answer = models.CharField()


class MultipleChoice(Question):
    num_of_options = models.PositiveSmallIntegerField()

    def get_text(self):
        return self.question_text


class TrueFalse(Question):
    answer = models.BooleanField()


class QuestionAnswer(models.Model):
    user = models.ForeignKey(User)
    question = models.ForeignKey(Question)
    correct = models.BooleanField()


class Player(models.Model):
    skill = models.DecimalField(max_digits=3, decimal_places=3)
