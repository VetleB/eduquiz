from django.test import TestCase
from quiz.models import *
from django.contrib.auth.admin import User
import random


class TextQuestionTestCase(TestCase):

    def setUp(self):
        TextQuestion.objects.create(
            question_text = 'TEST_QUESTION',
            answer = 'Answer',
        )

    def test_validation_ignores_capitalization(self):
        question = TextQuestion.objects.get()
        self.assertTrue(question.validate('ansWer'))
        question.answer = 'ANSWER'
        self.assertTrue(question.validate('ansWer'))

    def test_validation_ignores_special_characters(self):
        question = TextQuestion.objects.get()
        question.answer = 'this answer'
        self.assertTrue(question.validate('this-answer'))
        self.assertTrue(question.validate('this_answer'))
        self.assertTrue(question.validate('this.answer'))
        self.assertTrue(question.validate('this answer'))
        self.assertTrue(question.validate('thisanswer'))
        question.answer = 'this-answer'
        self.assertTrue(question.validate('this answer'))
        question.answer = 'this_answer'
        self.assertTrue(question.validate('this answer'))
        question.answer = 'thisanswer'
        self.assertTrue(question.validate('this answer'))

    def test_validation_not_ignores_numbers(self):
        question = TextQuestion.objects.get()
        question.answer = 'this answer'
        self.assertFalse(question.validate('this0answer'))
        question.answer = 'this answer1'
        self.assertFalse(question.validate('this answer'))


class NumberQuestionTestCase(TestCase):

    def setUp(self):
        NumberQuestion.objects.create(
            question_text = 'TEST_QUESTION',
            answer = '1.000',
        )

    def test_validation_of_correct_answer(self):
        question = NumberQuestion.objects.get()
        question.answer = '1231231.45'
        self.assertTrue(question.validate('1231231.45'))
        self.assertFalse(question.validate('12312314.5'))

    def test_validation_of_float_when_answer_is_int(self):
        question = NumberQuestion.objects.get()
        question.answer = '42'
        self.assertTrue(question.validate('42.0'))
        question.answer = 'AB'
        self.assertTrue(question.validate('AB.0'))

    def test_validation_of_comma_as_decimal_mark(self):
        question = NumberQuestion.objects.get()
        self.assertTrue(question.validate('1.000'))
        self.assertTrue(question.validate('1,000'))

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
        question.answer = '1.001'
        self.assertFalse(question.validate('.001'))

    def test_validation_of_trailing_zeros(self):
        question = NumberQuestion.objects.get()
        question.answer = '0.1'
        self.assertTrue(question.validate('0.10'))
        self.assertFalse(question.validate('0.10010'))

    def test_validation_of_zero(self):
        question = NumberQuestion.objects.get()
        question.answer = '0'
        self.assertTrue(question.validate('0'))
        self.assertTrue(question.validate('0.'))
        self.assertTrue(question.validate('.'))
        self.assertTrue(question.validate('.0'))

    def test_validation_of_leading_zeroes(self):
        question = NumberQuestion.objects.get()
        question.answer = '10'
        self.assertTrue(question.validate('010'))

    def test_validation_of_hexadecimal_capitalization(self):
        question = NumberQuestion.objects.get()
        question.answer = 'aB3.bF1'
        self.assertTrue(question.validate('ab3.bf1'))
        self.assertTrue(question.validate('AB3.BF1'))
        self.assertTrue(question.validate('Ab3.Bf1'))
        question.answer = 'AB123ef'
        self.assertTrue(question.validate('Ab123eF'))


class MultipleChoiceTestCase(TestCase):

    def setUp(self):
        question = MultipleChoiceQuestion.objects.create(
            question_text = 'TEST_QUESTION',
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
        question = MultipleChoiceQuestion.objects.get(question_text='TEST_QUESTION')
        correctAnswers = MultipleChoiceAnswer.objects.filter(
            question = question,
            correct = True,
        )
        correctAnswer = correctAnswers[0]
        response = question.answerFeedback(correctAnswer.id)
        json = {
            'answer': correctAnswer.id,
            'correct': [correctAnswer.id for correctAnswer in correctAnswers],
            'answeredCorrect': True,
        }
        self.assertEqual(response, json)

    def testAnswerIncorrect(self):
        question = MultipleChoiceQuestion.objects.get(question_text='TEST_QUESTION')
        wrongAnswers = MultipleChoiceAnswer.objects.filter(
            question = question,
            correct = False,
            )
        correctAnswers = MultipleChoiceAnswer.objects.filter(
            question = question,
            correct = True,
            )
        wrongAnswer = wrongAnswers[0]
        response = question.answerFeedback(wrongAnswer.id)
        json = {
            'answer': wrongAnswer.id,
            'correct': [correctAnswer.id for correctAnswer in correctAnswers],
            'answeredCorrect': False,
        }
        self.assertEqual(response, json)


class TrueFalseTestCase(TestCase):

    def setUp(self):
        question = TrueFalseQuestion.objects.create(
            question_text = 'TEST_QUESTION',
            answer = True,
        )

    def testAnswerCorrect(self):
        question = TrueFalseQuestion.objects.get(question_text='TEST_QUESTION')
        response = question.answerFeedback(True)
        json = {
            'answer': True,
            'correct': True,
            'answeredCorrect': True,
        }
        self.assertEqual(response, json)

    def testAnswerIncorrect(self):
        question = TrueFalseQuestion.objects.get(question_text='TEST_QUESTION')
        response = question.answerFeedback(False)
        json = {
            'answer': False,
            'correct': True,
            'answeredCorrect': False,
        }
        self.assertEqual(response, json)
