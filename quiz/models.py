from django.db import models
from django.contrib.auth.admin import User
from django.utils import timezone
from re import match
from django.db.models import Count
from datetime import datetime


class Achievement(models.Model):
    name = models.CharField(max_length=50, verbose_name='Title', default='')
    badge = models.ImageField(verbose_name='Badge', blank=True, null=True)

    def is_achieved(self, player):
        for prop in self.property_set.all():
            try:
                PropertyUnlock.objects.get(player=player, prop=prop)
            except PropertyUnlock.DoesNotExist:
                return False
        return True

    def update(self, player):
        if self.is_achieved(player):
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
    def is_unlocked(self, player):
        return True

    def update(self, player):
        if self.is_unlocked(player):
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

    def set_rating(self, rating):
        PlayerRating.set_rating(self, rating)

    def subject_answers(self):
        counts = []
        titles = []

        query = PlayerAnswer.objects.filter(player=self).values('question__topic__subject')\
            .annotate(count=Count('question__topic__subject'))

        for element in query:
            sub = Subject.objects.get(pk=element['question__topic__subject'])
            count = element['count']
            counts.append(count)
            titles.append(sub.title)

        return counts, titles

    def rating_list(self, subject=None):
        if subject is None:
            subject = self.subject()
        qset = PlayerAnswer.objects.filter(player=self, question__topic__subject=subject)\
            .values_list('rating', 'answer_date').order_by('answer_date')

        return [float(a[0]) for a in qset], [datetime.strftime(a[1], '%d %B') for a in qset]

    def subject(self):
        try:
            return PlayerTopic.objects.filter(player=self).first().topic.subject
        except AttributeError:
            return None

    def rating(self):
        return PlayerRating.get_rating(self)

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
        question_k = 8
        player_k = 16
        rating_cap = 150

        rating = float(self.rating())
        question_rating = float(question.rating)

        if rating - question_rating < rating_cap:
            new_rating = rating + player_k * (win - self.exp(rating, question_rating))
            question.rating = question_rating + question_k * ((1-win) - self.exp(question_rating, rating))
            question.save()
            PlayerRating.set_rating(self, new_rating)

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

    def virtual_rating(self, topics):
        """
        Return rating adjusted up if player is on win streak, down if on loss streak.

        :param topics: List of PlayerTopic objects
        :type topics: list

        :return: Player's adjusted rating
        :rtype: float
        """
        virtual_k = 10
        virtual_c = 5

        # Get the virtual_c latest answers that are not reports
        # (report_skip must equal False) and in/decrease rating thereafter
        answers = [pa for pa in PlayerAnswer.objects.filter(player=self, question__topic__in=topics)
                   .order_by('-answer_date') if pa.report_skip is not True][:virtual_c]

        virtual = sum([virtual_k if answer.result else -virtual_k for answer in answers])
        return PlayerRating.get_rating(self) + virtual

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

    def high_score(self):
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
    def get_rating_object(player, subject=None):
        if subject is None:
            subject = player.subject()
        if not subject:
            return None
        try:
            return PlayerRating.objects.get(player=player, subject=subject)
        except PlayerRating.DoesNotExist:
            return PlayerRating.objects.create(player=player, subject=subject)

    @staticmethod
    def get_rating(player, subject=None):
        """
        Get rating of a player in a subject

        :param player: player for whom rating is wanted
        :type player: Player object

        :param subject: subject for which player's rating is wanted
        :type subject: Subject object

        :return: Player's rating in subject
        :rtype: float
        """
        player_rating = PlayerRating.get_rating_object(player, subject)
        if player_rating:
            return player_rating.rating
        else:
            return 1200

    @staticmethod
    def set_rating(player, rating, subject=None):
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
        player_rating = PlayerRating.get_rating_object(player, subject)
        player_rating.rating = rating
        player_rating.save()


class Question(models.Model):
    question_text = models.TextField(max_length=200, verbose_name='Question')
    creator = models.ForeignKey(User, blank=True, null=True)
    creation_date = models.DateTimeField(default=timezone.now, verbose_name='Date')
    rating = models.DecimalField(default=1200, max_digits=8, decimal_places=3, verbose_name='Rating')
    topic = models.ForeignKey(Topic, null=True, blank=True)

    def __str__(self):
        return self.question_text

    def answer_to_list(self):
        """
        Returns the answer as a text string in a list

        :return: Answer
        :rtype: str
        """
        return []
      

class TextQuestion(Question):
    answer = models.CharField(max_length=50, verbose_name='Answer')

    def __str__(self):
        return self.question_text

    def validate(self, in_answer):
        """
        Determines whether a text answer is right or wrong

        :param in_answer: Answer to be validated
        :type in_answer: string

        :return: Whether answer is right or not
        :rtype: boolean
        """
        user_answer = in_answer.strip().casefold()
        correct_answer = self.answer.strip().casefold()

        # Fjerner alt som ikke er alfanumerisk
        user_answer = ''.join([c for c in user_answer if c.isalnum()])
        correct_answer = ''.join([c for c in correct_answer if c.isalnum()])

        return user_answer == correct_answer

    def answer_feedback_raw(self, answer):
        return self.answer_feedback(answer)

    def answer_feedback(self, answer):
        """
        Validates answer and returns feedback as JSON-object

        :param answer: Answer to be validated
        :type answer: string

        :return: JSON-object
        :rtype: dict
        """
        answered_correct = self.validate(answer)
        return {
            'answer': answer,
            'correct': self.answer,
            'answered_correct': answered_correct,
        }

    def answer_to_list(self):
        """
        Returns the answer as a text string in a list

        :return: Answer
        :rtype: list
        """
        return [self.answer]


class NumberQuestion(Question):
    answer = models.CharField(max_length=50, verbose_name='Answer')

    def __str__(self):
        return self.question_text

    def validate(self, in_answer):
        """
        Determines whether a number answer is right or wrong

        :param in_answer: Answer to be validated
        :type in_answer: string

        :return: Whether answer is right or not
        :rtype: boolean
        """
        if in_answer == '':
            return False

        user_answer = in_answer.casefold().strip().replace(',', '.')
        correct_answer = self.answer.casefold().strip().replace(',', '.')

        # Removes leading zeros
        while len(user_answer) > 1 and user_answer[0] == '0':
            user_answer = user_answer[1:]

        # If no integer part, set it to '0'
        if user_answer[0] == '.':
            user_answer = '0' + user_answer

        # If answer not a decimal, check if user's answer only has zeros in the decimal part and compare
        if '.' not in correct_answer:
            if '.' in user_answer:
                spl = user_answer.split('.')
                if match(r'^0*$', spl[1]):
                    return spl[0] == correct_answer
                return False
            return user_answer == correct_answer

        correct_num_of_decimals = len(correct_answer.split('.')[1])

        if '.' in user_answer:
            user_answer = user_answer.split('.')
            num_of_decimals = len(user_answer[1])

            # Adds zeros to decimal part to get correct length
            if num_of_decimals < correct_num_of_decimals:
                user_answer[1] += ''.join(['0']*(correct_num_of_decimals-num_of_decimals))

            # Remove trailing zeros to get correct length
            if num_of_decimals > correct_num_of_decimals:
                extra = user_answer[1][correct_num_of_decimals:]
                zero_match = match(r'^0*$', extra)
                if zero_match:
                    user_answer[1] = user_answer[1][0:correct_num_of_decimals]

            user_answer = '.'.join(user_answer)
        else:
            user_answer += '.' + ''.join(['0']*correct_num_of_decimals)

        # Make sure user's answer is on right format
        pattern_match = bool(match(r'^0*[0-9a-f]*[.][0-9a-f]*$', user_answer))
        # Compare user's answer with the actual answer
        return (user_answer == correct_answer) and pattern_match

    def answer_feedback_raw(self, answer):
        return self.answer_feedback(answer)

    def answer_feedback(self, answer):
        """
        Validates answer and returns feedback as JSON-object

        :param answer: Answer to be validated
        :type answer: string

        :return: JSON-object
        :rtype: dict
        """
        answered_correct = self.validate(answer)
        return {
            'answer': answer,
            'correct': self.answer,
            'answered_correct': answered_correct,
        }

    def answer_to_list(self):
        """
        Returns the answer as a text string in a list

        :return: Answer
        :rtype: list
        """
        return [self.answer]


class TrueFalseQuestion(Question):
    answer = models.BooleanField(verbose_name='Answer')

    def __str__(self):
        return self.question_text

    def answer_feedback_raw(self, answer):
        return self.answer_feedback(answer.capitalize() == 'True')

    def answer_feedback(self, answer):
        """
        Validates answer and returns feedback as JSON-object

        :param answer: Answer to be validated
        :type answer: boolean

        :return: JSON-object
        :rtype: dict
        """
        answered_correct = answer == self.answer
        return {
            'answer': answer,
            'correct': self.answer,
            'answered_correct': answered_correct,
        }

    def answer_to_list(self):
        """
        Returns the answer as a text string in a list

        :return: Answer
        :rtype: list
        """
        return [str(self.answer)]


class MultipleChoiceQuestion(Question):

    def __str__(self):
        return self.question_text

    def answer_feedback_raw(self, answer):
        try:
            return self.answer_feedback(int(answer))
        except ValueError:
            return self.answer_feedback(1)

    def answer_feedback(self, answer_id):
        """
        Validates answer and returns feedback as JSON-object

        :param answer_id: Answer to be validated
        :type answer_id: int

        :return: JSON-object
        :rtype: dict
        """
        answer = MultipleChoiceAnswer.objects.get(id=answer_id)
        answered_correct = answer.correct
        answers = MultipleChoiceAnswer.objects.filter(question=self.id, correct=True)
        answer_ids = [answer.id for answer in answers]
        return {
            'answer': answer_id,
            'correct': answer_ids,
            'answered_correct': answered_correct,
        }

    def answer_to_list(self):
        """
        Returns the answers as a list of strings, indicating the correct one

        :return: Answer
        :rtype: list
        """

        return_list = []

        for ans in MultipleChoiceAnswer.objects.filter(question=self):
            tmp = '-' + ans.answer
            if ans.correct:
                tmp += ' -> Correct'
            return_list.append(tmp + '\n')

        return return_list


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


class PropAnsweredQuestionInSubject(Property):
    number = models.IntegerField(default=0, verbose_name="Number of answers")
    subject = models.ForeignKey(Subject, verbose_name="Subject")

    def is_unlocked(self, player):
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
