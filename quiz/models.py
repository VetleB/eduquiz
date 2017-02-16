from django.db import models
from django.contrib.auth.admin import User
from django.utils import timezone


class Player(models.Model):
    skill_lvl = models.DecimalField(max_digits=3, decimal_places=3, verbose_name='Skill Lvl')
    user = models.ForeignKey(User)


class Category(models.Model):
    title = models.TextField(max_length=100, verbose_name='Title')


class Subject(models.Model):
    title = models.TextField(max_length=100, verbose_name='Title')
    code = models.TextField(max_length=10, verbose_name='Code')
    category = models.ForeignKey(Category)


class Topic(models.Model):
    title = models.TextField(max_length=100, verbose_name='Title')
    subject = models.ForeignKey(Subject)


class Question(models.Model):
    question_text = models.TextField(max_length=200, verbose_name='Question')
    creator = models.ForeignKey(Player)
    creation_date = models.DateTimeField(default=timezone.now, verbose_name='Date')
    difficulty = models.DecimalField(max_digits=3, decimal_places=3, verbose_name='Difficulty')


class QuestionTopic(models.Model):
    topic = models.ForeignKey(Topic)
    question = models.ForeignKey(Question)


class TextQuestion(Question):
    answer = models.CharField(max_length=50, verbose_name='Answer')


class TrueFalseQuestion(Question):
    answer = models.BooleanField(verbose_name='Answer')


class MultipleChoiceQuestion(Question):
    pass


class MultipleChoiceAnswer(models.Model):
    answer = models.CharField(max_length=100, verbose_name='Answer')
    correct = models.BooleanField(verbose_name='Correct')


class PlayerAnswer(models.Model):
    player = models.ForeignKey(Player)
    question = models.ForeignKey(Question)
    result = models.BooleanField(verbose_name='Result')
    answer_date = models.DateTimeField(default=timezone.now, verbose_name='Date')
