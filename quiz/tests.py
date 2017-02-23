from django.test import TestCase
from quiz.models import *

# Create your tests here.


class TextQuestionTestCase(TestCase):
    def test_validation_of_correct_answer(self):
        question = TextQuestion()
        question.answer = '1.450'
        self.assertTrue(question.validate('1.45'))
        self.assertTrue(question.validate('1.450'))
        self.assertFalse(question.validate('1.460'))
        self.assertFalse(question.validate('2.450'))
        self.assertFalse(question.validate('11.455'))

    def test_validation_of_comma_as_decimal_mark(self):
        question = TextQuestion()
        question.answer = '1.000'
        self.assertTrue(question.validate('1.000'))
        self.assertTrue(question.validate('1,000'))
        self.assertTrue(question.validate('1,'))

    def test_validation_of_answer_without_decimal_part(self):
        question = TextQuestion()
        question.answer = '1.000'
        self.assertTrue(question.validate('1'))
        self.assertTrue(question.validate('1.'))

    def test_validation_of_answer_without_integer_part(self):
        question = TextQuestion()
        question.answer = '0.001'
        self.assertTrue(question.validate('.001'))
        self.assertFalse(question.validate('001'))

    def test_validation_of_too_many_decimals(self):
        question = TextQuestion()
        question.answer = '1.000'
        self.assertFalse(question.validate('1.0001'))
        self.assertTrue(question.validate('1.0000'))

    def test_validation_of_too_few_decimals(self):
        question = TextQuestion()
        question.answer = '1.000'
        self.assertTrue(question.validate('1.'))
        self.assertTrue(question.validate('1.0'))
        self.assertTrue(question.validate('1.00'))

    def test_validation_of_zero(self):
        question = TextQuestion()
        question.answer = '0.000'
        self.assertTrue(question.validate('0'))
        self.assertTrue(question.validate('0.'))
        self.assertTrue(question.validate('.'))
        self.assertTrue(question.validate('.000'))
        self.assertTrue(question.validate('0.00000000000'))

    def test_validation_of_leading_zeroes(self):
        question = TextQuestion()
        question.answer = '10.000'
        self.assertTrue(question.validate('010'))
        self.assertTrue(question.validate('00000000000010'))
        self.assertTrue(question.validate('010.000'))

    def test_validation_of_hexadecimal_capitalization(self):
        question = TextQuestion()
        question.answer = 'aB3.bF1'
        self.assertTrue(question.validate('ab3.bf1'))
        self.assertTrue(question.validate('AB3.BF1'))
        self.assertTrue(question.validate('Ab3.Bf1'))
        self.assertTrue(question.validate('aB3.bF1'))
