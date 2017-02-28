from django.test import TestCase
from quiz.models import *
from django.contrib.auth.admin import User
import random


class TextQuestionTestCase(TestCase):

    def setUp(self):
        player = Player.objects.create(
            user = User.objects.create(),
        )
        question = TextQuestion.objects.create(
            question_text = 'TEST_QUESTION',
            creator = player,
            difficulty = 0.0,
            answer = 'Answer',
        )

    def test_validation_ignores_capitalization(self):
        question = TextQuestion.objects.get()
        self.assertTrue(question.validate('ansWer'))


class NumberQuestionTestCase(TestCase):

    def setUp(self):
        player = Player.objects.create(
            user = User.objects.create(),
        )
        question = NumberQuestion.objects.create(
            question_text = 'TEST_QUESTION',
            creator = player,
            difficulty = 0.0,
            answer = '1.000',
        )

    def test_validation_of_correct_answer(self):
        question = NumberQuestion.objects.get()
        question.answer = '1.45'
        self.assertTrue(question.validate('1.45'))
        self.assertFalse(question.validate('1.46'))
        question.answer = '42'
        self.assertTrue(question.validate('42'))

    def test_validation_of_float_when_answer_is_int(self):
        question = NumberQuestion.objects.get()
        question.answer = '42'
        self.assertTrue(question.validate('42.0'))

    def test_validation_of_comma_as_decimal_mark(self):
        question = NumberQuestion.objects.get()
        self.assertTrue(question.validate('1.000'))
        self.assertTrue(question.validate('1,000'))
        self.assertTrue(question.validate('1,'))

    def test_validation_of_superfluous_spaces(self):
        question = NumberQuestion.objects.get()
        self.assertTrue(question.validate(' 1.000'))
        self.assertTrue(question.validate('1.000 '))
        self.assertTrue(question.validate(' 1.000 '))

    def test_validation_of_answer_without_decimal_part(self):
        question = NumberQuestion.objects.get()
        self.assertTrue(question.validate('1'))
        self.assertTrue(question.validate('1.'))

    def test_validation_of_answer_without_integer_part(self):
        question = NumberQuestion.objects.get()
        question.answer = '0.001'
        self.assertTrue(question.validate('.001'))
        self.assertFalse(question.validate('001'))

    def test_validation_of_too_many_decimals(self):
        question = NumberQuestion.objects.get()
        self.assertFalse(question.validate('1.0001'))
        self.assertTrue(question.validate('1.0000'))

    def test_validation_of_too_few_decimals(self):
        question = NumberQuestion.objects.get()
        self.assertTrue(question.validate('1.'))
        self.assertTrue(question.validate('1.0'))
        self.assertTrue(question.validate('1.00'))

    def test_validation_of_zero(self):
        question = NumberQuestion.objects.get()
        question.answer = '0.000'
        self.assertTrue(question.validate('0'))
        self.assertTrue(question.validate('0.'))
        self.assertTrue(question.validate('.'))
        self.assertTrue(question.validate('.000'))
        self.assertTrue(question.validate('0.00000000000'))

    def test_validation_of_leading_zeroes(self):
        question = NumberQuestion.objects.get()
        question.answer = '10.000'
        self.assertTrue(question.validate('010'))
        self.assertTrue(question.validate('00000000000010'))
        self.assertTrue(question.validate('010.000'))

    def test_validation_of_hexadecimal_capitalization(self):
        question = NumberQuestion.objects.get()
        question.answer = 'aB3.bF1'
        self.assertTrue(question.validate('ab3.bf1'))
        self.assertTrue(question.validate('AB3.BF1'))
        self.assertTrue(question.validate('Ab3.Bf1'))
        self.assertTrue(question.validate('aB3.bF1'))


class MultipleChoiceTestCase(TestCase):

    def setUp(self):
        player = Player.objects.create(
            user = User.objects.create(),
        )
        question = MultipleChoiceQuestion.objects.create(
            question_text = 'TEST_QUESTION',
            creator = player,
            difficulty = 0.0,
        )
        answers = [MultipleChoiceAnswer.objects.create(
                question = question,
                answer = 'TEST_ANSWER_%s' % ans,
                correct = False,
            ) for ans in ('A', 'B', 'C', 'D')]
        trueAnswer = answers[random.randint(0,3)]
        trueAnswer.correct = True
        trueAnswer.save()


    def testAnswerCorrect(self):
        question = MultipleChoiceQuestion.objects.get()
        correctAnswers = MultipleChoiceAnswer.objects.filter(correct=True)
        correctAnswer = correctAnswers[0]
        response = question.answerFeedback(correctAnswer.id)
        json = {
            'answer': correctAnswer.id,
            'correct': [correctAnswer.id for correctAnswer in correctAnswers],
            'answeredCorrect': True,
        }
        self.assertEqual(response, json)

    def testAnswerIncorrect(self):
        question = MultipleChoiceQuestion.objects.get()
        wrongAnswers = MultipleChoiceAnswer.objects.filter(correct=False)
        correctAnswers = MultipleChoiceAnswer.objects.filter(correct=True)
        wrongAnswer = wrongAnswers[0]
        response = question.answerFeedback(wrongAnswer.id)
        json = {
            'answer': wrongAnswer.id,
            'correct': [correctAnswer.id for correctAnswer in correctAnswers],
            'answeredCorrect': False,
        }
        self.assertEqual(response, json)


class CategorySubjectTopicTestCase(TestCase):

    def setUp(self):
        category = Category.objects.create(
            title = 'TEST_CATEGORY',
        )
        subject = Subject.objects.create(
            title = 'TEST_SUBJECT',
            short = 'TS',
            code = 'TST1001',
            category = category
        )
        topic = Topic.objects.create(
            title = 'TEST_TOPIC',
            subject = subject,
        )
