from django.test import TestCase
from quiz.models import *
from django.contrib.auth.admin import User
import random
import json
from django.test import Client


class TextQuestionTestCase(TestCase):

    def setUp(self):
        TextQuestion.objects.create(
            question_text='TEST_QUESTION',
            answer='Answer',
        )

    def test_str_returns_question_text(self):
        tq = TextQuestion.objects.get()
        self.assertEqual(str(tq), 'TEST_QUESTION')

    def test_raw_feedback(self):
        tq = TextQuestion.objects.get()
        self.assertEqual(tq.answer_feedback_raw('fail'),
                         {'answer': 'fail', 'correct': 'Answer', 'answered_correct': False})

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
            question_text='TEST_QUESTION',
            answer='1.000',
        )

    def test_str_returns_question_text(self):
        q = NumberQuestion.objects.get()
        self.assertEqual(str(q), 'TEST_QUESTION')

    def test_raw_feedback(self):
        nq = NumberQuestion.objects.get()
        self.assertEqual(nq.answer_feedback_raw('2'), {'answer': '2', 'correct': '1.000', 'answered_correct': False})

    def test_empty_returns_false(self):
        question = NumberQuestion.objects.get()
        self.assertFalse(question.validate(''))

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

    def test_validation_of_answer_without_decimal_part2(self):
        question = NumberQuestion.objects.get()
        question.answer = '133769'
        self.assertTrue(question.validate('133769'))
        self.assertTrue(question.validate('133769.'))
        self.assertFalse(question.validate('1.33769'))
        self.assertFalse(question.validate('1.3376.9'))

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
            question_text='TEST_QUESTION',
        )
        answers = [MultipleChoiceAnswer.objects.create(
                question=question,
                answer='TEST_ANSWER_%s' % ans,
                correct=False,
            ) for ans in ('A', 'B', 'C', 'D')]
        true_answer = answers[random.randint(0, 3)]
        true_answer.correct = True
        true_answer.save()

    def test_str_returns_question_text(self):
        q = MultipleChoiceQuestion.objects.get()
        self.assertEqual(str(q), 'TEST_QUESTION')

    def test_raw_feedback_valid_id(self):
        mcq = MultipleChoiceQuestion.objects.get()
        correct_answers = MultipleChoiceAnswer.objects.filter(
            question=mcq,
            correct=True,
        )
        correct_answer = correct_answers[0]
        self.assertEqual(mcq.answer_feedback_raw(str(correct_answer.id)),
                         {'answer': correct_answer.id,
                          'correct': [correctAnswer.id for correctAnswer in correct_answers], 'answered_correct': True})

    def test_raw_feedback_invalid_id(self):
        mcq = MultipleChoiceQuestion.objects.get()
        correct_answers = MultipleChoiceAnswer.objects.filter(
            question=mcq,
            correct=True,
        )
        correct_answer = correct_answers[0]
        answered_correct = True if correct_answer.id == 1 else False
        self.assertEqual(mcq.answer_feedback_raw("fail"),
                         {'answer': 1, 'correct': [correctAnswer.id for correctAnswer in correct_answers],
                          'answered_correct': answered_correct})

    def testAnswerCorrect(self):
        question = MultipleChoiceQuestion.objects.get(question_text='TEST_QUESTION')
        correct_answers = MultipleChoiceAnswer.objects.filter(
            question=question,
            correct=True,
        )
        correct_answer = correct_answers[0]
        response = question.answer_feedback(correct_answer.id)
        json = {
            'answer': correct_answer.id,
            'correct': [correctAnswer.id for correctAnswer in correct_answers],
            'answered_correct': True,
        }
        self.assertEqual(response, json)

    def testAnswerIncorrect(self):
        question = MultipleChoiceQuestion.objects.get(question_text='TEST_QUESTION')
        wrong_answers = MultipleChoiceAnswer.objects.filter(
            question=question,
            correct=False,
            )
        correct_answers = MultipleChoiceAnswer.objects.filter(
            question=question,
            correct=True,
            )
        wrong_answer = wrong_answers[0]
        response = question.answer_feedback(wrong_answer.id)
        json = {
            'answer': wrong_answer.id,
            'correct': [correctAnswer.id for correctAnswer in correct_answers],
            'answered_correct': False,
        }
        self.assertEqual(response, json)


class TrueFalseTestCase(TestCase):

    def setUp(self):
        TrueFalseQuestion.objects.create(
            question_text='TEST_QUESTION',
            answer=True,
        )

    def test_str_returns_question_text(self):
        q = TrueFalseQuestion.objects.get()
        self.assertEqual(str(q), 'TEST_QUESTION')

    def test_raw_feedback(self):
        tfq = TrueFalseQuestion.objects.get()
        self.assertEqual(tfq.answer_feedback_raw('False'),
                         {'answer': False, 'correct': True, 'answered_correct': False})

    def testAnswerCorrect(self):
        question = TrueFalseQuestion.objects.get(question_text='TEST_QUESTION')
        response = question.answer_feedback(True)
        json = {
            'answer': True,
            'correct': True,
            'answered_correct': True,
        }
        self.assertEqual(response, json)

    def testAnswerIncorrect(self):
        question = TrueFalseQuestion.objects.get(question_text='TEST_QUESTION')
        response = question.answer_feedback(False)
        json = {
            'answer': False,
            'correct': True,
            'answered_correct': False,
        }
        self.assertEqual(response, json)


class AchievementTestCase(TestCase):

    def setUp(self):
        achievement = Achievement.objects.create(name='TEST_ACHIEVEMENT')
        prop = Property.objects.create(name='TEST_PROPERTY')
        trigger = Trigger.objects.create(name='TEST_TRIGGER')
        title = Title.objects.create(title='TEST_TITLE')
        user = User.objects.create(username='TEST_USER')
        Player.objects.create(user=user)

        trigger.properties.add(prop)
        prop.achievements.add(achievement)
        title.achievement = achievement

        trigger.save()
        prop.save()
        title.save()

    def test_str_returns_name(self):
        achievement = Achievement.objects.get()
        self.assertEqual(str(achievement), 'TEST_ACHIEVEMENT')

    def test_is_achieved_returns_false_when_not_all_props_checked(self):
        achievement = Achievement.objects.get()
        player = Player.objects.get()
        self.assertFalse(achievement.is_achieved(player))

    def testTrigger(self):
        player = Player.objects.get()
        prop = Property.objects.get(name='TEST_PROPERTY')

        Trigger.objects.get(name='TEST_TRIGGER').trigger(player)

        property_unlocks = PropertyUnlock.objects.filter(player=player, prop=prop)

        self.assertEqual(property_unlocks.count(), 1)

    def testAchieve(self):
        player = Player.objects.get()
        achievement = Achievement.objects.get(name='TEST_ACHIEVEMENT')

        Trigger.objects.get(name='TEST_TRIGGER').trigger(player)

        achievement_unlock = AchievementUnlock.objects.filter(player=player, achievement=achievement)

        self.assertEqual(achievement_unlock.count(), 1)

    def testTitle(self):
        player = Player.objects.get()
        title = Title.objects.get(title='TEST_TITLE')

        Trigger.objects.get(name='TEST_TRIGGER').trigger(player)

        title_unlock = TitleUnlock.objects.filter(player=player, title=title)

        self.assertEqual(title_unlock.count(), 1)


class TitleTestCase(TestCase):

    def setUp(self):
        achievement = Achievement.objects.create(name='TEST_ACHIEVEMENT')
        Title.objects.create(
            title='TEST_TITLE',
            achievement=achievement,
        )

    def test_str_returns_title(self):
        title = Title.objects.get()
        self.assertEqual(str(title), 'TEST_TITLE')


class PlayerTestCase(TestCase):

    def setUp(self):
        user = User.objects.create(username='TEST_USER')
        Player.objects.create(user=user)

    def test_str_returns_username(self):
        player = Player.objects.get()
        self.assertEqual(str(player), 'TEST_USER')


class PropertyTestCase(TestCase):

    def setUp(self):
        Property.objects.create(name='TEST_PROPERTY')

    def test_str_returns_name(self):
        prop = Property.objects.get()
        self.assertEqual(str(prop), 'TEST_PROPERTY')


class PropAnsweredQuestionInSubjectTestCase(TestCase):

    def setUp(self):
        cat = Category.objects.create(title='TEST_CATEGORY')
        sub = Subject.objects.create(
            title='TEST_SUBJECT',
            short='TS',
            code='TS1234',
            category=cat,
        )
        topic = Topic.objects.create(
            title='TEST_TOPIC',
            subject=sub,
        )
        PropAnsweredQuestionInSubject.objects.create(
            number=1,
            subject=sub,
        )
        user = User.objects.create(username='TEST_USER')
        Player.objects.create(user=user)
        Question.objects.create(
            question_text='TEST_QUESTION_TEXT',
            topic=topic,
        )

    def test_str_returns_number_in_title(self):
        prop = PropAnsweredQuestionInSubject.objects.get()
        self.assertEqual(str(prop), '1 in TEST_SUBJECT')

    def test_is_unlocked(self):
        prop = PropAnsweredQuestionInSubject.objects.get()
        player = Player.objects.get()
        self.assertFalse(prop.is_unlocked(player))
        question = Question.objects.get()
        PlayerAnswer.objects.create(
            player=player,
            question=question,
            result=True,
        )
        self.assertTrue(prop.is_unlocked(player))

    def test_does_not_exist_not_thrown_on_update(self):
        prop = PropAnsweredQuestionInSubject.objects.get()
        player = Player.objects.get()
        self.assertEqual(prop.update(player), None)


class TriggerTestCase(TestCase):

    def setUp(self):
        Trigger.objects.create(name='TEST_TRIGGER')

    def test_str_returns_name(self):
        trigger = Trigger.objects.get()
        self.assertEqual(str(trigger), 'TEST_TRIGGER')


class CategoryTestCase(TestCase):

    def setUp(self):
        Category.objects.create(title='TEST_CATEGORY')

    def test_str_returns_name(self):
        cat = Category.objects.get()
        self.assertEqual(str(cat), 'TEST_CATEGORY')


class SubjectTestCase(TestCase):

    def setUp(self):
        cat = Category.objects.create(title='TEST_CATEGORY')
        Subject.objects.create(
            title='TEST_SUBJECT',
            short='TS',
            code='TS1234',
            category=cat,
        )

    def test_str_returns_code_and_title(self):
        sub = Subject.objects.get()
        self.assertEqual(str(sub), 'TS1234 - TEST_SUBJECT')


class TopicTestCase(TestCase):

    def setUp(self):
        cat = Category.objects.create(title='TEST_CATEGORY')
        sub = Subject.objects.create(
            title='TEST_SUBJECT',
            short='TSUB',
            code='TS1234',
            category=cat,
        )
        Topic.objects.create(
            title='TEST_TOPIC',
            subject=sub,
        )

    def test_str_returns_name(self):
        topic = Topic.objects.get()
        self.assertEqual(str(topic), 'TEST_TOPIC')


class MultipleChoiceAnswerTestCase(TestCase):

    def setUp(self):
        mc = MultipleChoiceQuestion.objects.create(
            question_text='TEST_MC'

        )
        MultipleChoiceAnswer.objects.create(question=mc, answer='TEST_MC_ANS', correct=True)

    def test_str_returns_name(self):
        mca = MultipleChoiceAnswer.objects.get()
        self.assertEqual(str(mca), 'TEST_MC_ANS')


class RatingTestCase(TestCase):

    def setUp(self):
        user = User.objects.create(

        )
        player = Player.objects.create(
            user=user,
        )
        category = Category.objects.create(
            title="test_category",
        )
        subject = Subject.objects.create(
            title="test_subject",
            category=category,
        )
        topic = Topic.objects.create(
            title="test_topic",
            subject=subject,
        )
        Question.objects.create(
            topic=topic,
        )
        PlayerTopic.objects.create(
            player=player,
            topic=topic,
        )

    def test_rating_no_topic(self):
        Topic.objects.get().delete()
        player = Player.objects.get()
        self.assertEqual(PlayerRating.get_rating_object(player), None)

    def test_rating_change_on_correct(self):
        player = Player.objects.get()
        question = Question.objects.get()
        player.update(question, 1)
        self.assertTrue(question.rating < 1200)
        self.assertTrue(player.rating() > 1200)

    def test_rating_change_on_incorrect(self):
        player = Player.objects.get()
        question = Question.objects.get()
        player.update(question, 0)
        self.assertTrue(question.rating > 1200)
        self.assertTrue(player.rating() < 1200)

    def test_no_rating_change_above_cap(self):
        player = Player.objects.get()
        PlayerRating.set_rating(player, 1700)
        question = Question.objects.get()
        player.update(question, 0)
        self.assertTrue(question.rating == 1200)
        self.assertTrue(player.rating() == 1700)

    def test_virtual_rating_increase(self):
        player = Player.objects.get()
        question = Question.objects.get()
        PlayerAnswer.objects.create(
            player=player,
            question=question,
            result=True,
        )
        self.assertTrue(player.rating() < player.virtual_rating([question.topic]))

    def test_virtual_rating_decrease(self):
        player = Player.objects.get()
        question = Question.objects.get()
        PlayerAnswer.objects.create(
            player=player,
            question=question,
            result=False,
        )
        self.assertTrue(player.rating() > player.virtual_rating([question.topic]))

    def test_virtual_rating_increase_and_decrease(self):
        player = Player.objects.get()
        question = Question.objects.get()
        PlayerAnswer.objects.create(
            player=player,
            question=question,
            result=True,
        )
        PlayerAnswer.objects.create(
            player=player,
            question=question,
            result=False,
        )
        self.assertTrue(player.rating() == player.virtual_rating([question.topic]))


class RedirectTestCase(TestCase):
    TEST_USERNAME = 'TEST_USERNAME'
    TEST_PASS = 'TEST_PASSWORD'

    def setUp(self):
        self.client = Client()
        test_user = User.objects.create(
            username=self.TEST_USERNAME,
            password=self.TEST_PASS,
        )
        Player.objects.create(
            user=test_user,
        )
        PlayerTopic.objects.create(
            player=Player.objects.get(),
            topic=Topic.objects.create(
                title='TEST_TITLE',
                subject=Subject.objects.create(
                    title='TEST_SUBJECT',
                    short='TS',
                    code='TS-1234',
                    category=Category.objects.create(
                        title='TEST_CATEGORY'
                    )
                )
            )
        )

    def test_play_redirects_to_frontpage_when_not_signed_in(self):
        response = self.client.get('/quiz', follow=True)
        final_url = response.redirect_chain[-1]
        self.assertEqual(final_url[0], '/')

    def test_play_does_not_redirect_when_logged_in_with_topics(self):
        self.client.login(user=self.TEST_USERNAME, password=self.TEST_PASS)
        response = self.client.get('/quiz')
        self.assertEqual(response['location'], '/quiz/')


class StatsTestCase(TestCase):

    def setUp(self):
        category = Category.objects.create(title='TEST_CATEGORY')
        self.subjectA = Subject.objects.create(title='TEST_SUBJECT_A', category=category)
        self.subjectB = Subject.objects.create(title='TEST_SUBJECT_B', category=category)
        self.topicA = Topic.objects.create(title='TEST_TOPIC_A', subject=self.subjectA)
        self.topicB = Topic.objects.create(title='TEST_TOPIC_B', subject=self.subjectB)
        self.questionA = TrueFalseQuestion.objects\
            .create(question_text='TEST_QUESTION_A', answer=True, topic=self.topicA)
        self.questionB = TrueFalseQuestion.objects\
            .create(question_text='TEST_QUESTION_B', answer=True, topic=self.topicB)
        user_a = User.objects.create(username='TEST_USER_A')
        user_b = User.objects.create(username='TEST_USER_B')
        self.playerA = Player.objects.create(user=user_a)
        self.playerB = Player.objects.create(user=user_b)
        PlayerTopic.objects.create(player=self.playerA, topic=self.topicA)
        PlayerTopic.objects.create(player=self.playerB, topic=self.topicA)

    def test_highscore(self):
        self.playerA.set_rating(1300)
        self.playerB.set_rating(1250)
        self.assertEqual(self.subjectA.high_score(), [(1, 'TEST_USER_A', 1300), (2, 'TEST_USER_B', 1250)])

    def test_setRating(self):
        self.playerA.set_rating(1500)
        self.assertEqual(PlayerRating.get_rating(self.playerA), 1500)

    def test_ratingList(self):
        self.playerA.update(self.questionA, True)
        self.playerA.update(self.questionA, True)
        self.playerA.update(self.questionA, True)

        rating_list = self.playerA.rating_list()
        self.assertEqual(len(rating_list[0]), len(rating_list[1]), 3)

        a, b, c = rating_list[0]
        self.assertTrue(a < b < c)

    def test_ratingList2(self):
        self.playerA.update(self.questionA, False)
        self.playerA.update(self.questionA, False)
        self.playerA.update(self.questionA, False)

        rating_list = self.playerA.rating_list()
        a, b, c = rating_list[0]
        self.assertTrue(a > b > c)

    def test_subjectAnswers(self):
        self.playerA.update(self.questionA, False)
        self.playerA.update(self.questionA, True)
        self.playerA.update(self.questionB, False)
        self.playerA.update(self.questionB, True)
        self.playerA.update(self.questionB, True)

        self.assertEqual(self.playerA.subject_answers(), ([2, 3], ['TEST_SUBJECT_A', 'TEST_SUBJECT_B']))


class QuestionFormTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        category = Category.objects.create(title='TEST_CATEGORY')
        self.subject = Subject.objects.create(title='TEST_SUBJECT', category=category)
        self.topic = Topic.objects.create(title='TEST_TOPIC', subject=self.subject)
        self.user = User.objects.create_user(username='TEST_USER', password='TEST_PASSWORD')
        self.player = Player.objects.create(user=self.user)
        self.client.login(username='TEST_USER', password='TEST_PASSWORD')

    def test_create_question_page(self):
        response = self.client.get('/quiz/new/')
        self.assertEqual(response.status_code, 200)

    def test_not_authenticated(self):
        self.client.logout()
        response = self.client.post('/quiz/new/')
        self.assertEqual(response.status_code, 302)

    def test_create_multiple_choice_question(self):
        response = self.client.post('/quiz/new/multiplechoice/', {
            'question': 'TEST_QUESTION',
            'answer1': 'TEST_ANSWER_1',
            'answer2': 'TEST_ANSWER_2',
            'answer3': 'TEST_ANSWER_3',
            'answer4': 'TEST_ANSWER_4',
            'correct': 'Alt2',
            'rating': '5',
            'subject': self.subject.title,
            'topics': self.topic.title,
        })

        self.assertTrue(response.status_code, 302)
        self.assertTrue(response.url, '/quiz/new/')

    def test_create_multiple_choice_question_fail(self):
        response = self.client.post('/quiz/new/multiplechoice/', {
            'question': 'TEST_QUESTION',
            'answer1': 'TEST_ANSWER_1',
            'answer2': 'TEST_ANSWER_2',
            'answer3': 'TEST_ANSWER_3',
            'answer4': 'TEST_ANSWER_4',
            'rating': '5',
            'subject': self.subject.title,
            'topics': self.topic.title,
        })

        self.assertTrue(response.status_code, 200)

    def test_create_truefalse_question(self):
        response = self.client.post('/quiz/new/truefalse/', {
            'question': 'TEST_QUESTION',
            'correct': 'True',
            'rating': '5',
            'subject': self.subject.title,
            'topics': self.topic.title,
        })

        self.assertTrue(response.status_code, 302)
        self.assertTrue(response.url, '/quiz/new/')

    def test_create_truefalse_question_fail(self):
        response = self.client.post('/quiz/new/truefalse/', {
            'question': 'TEST_QUESTION',
            'rating': '5',
            'subject': self.subject.title,
            'topics': self.topic.title,
        })

        self.assertTrue(response.status_code, 200)

    def test_create_text_question(self):
        response = self.client.post('/quiz/new/text/', {
            'question': 'TEST_QUESTION',
            'answer': 'TEST_ANSWER',
            'text': 'True',
            'rating': '5',
            'subject': self.subject.title,
            'topics': self.topic.title,
        })

        self.assertTrue(response.status_code, 302)
        self.assertTrue(response.url, '/quiz/new/')

    def test_create_number_question(self):
        response = self.client.post('/quiz/new/text/', {
            'question': 'TEST_QUESTION',
            'answer': 'TEST_ANSWER',
            'text': 'False',
            'rating': '5',
            'subject': self.subject.title,
            'topics': self.topic.title,
        })

        self.assertTrue(response.status_code, 302)
        self.assertTrue(response.url, '/quiz/new/')

    def test_create_text_question_fail(self):
        response = self.client.post('/quiz/new/text/', {
            'question': 'TEST_QUESTION',
            'answer': 'TEST_ANSWER',
            'rating': '5',
            'subject': self.subject.title,
            'topics': self.topic.title,
        })

        self.assertTrue(response.status_code, 200)


class ViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        category = Category.objects.create(title='TEST_CATEGORY')
        self.subject = Subject.objects.create(title='TEST_SUBJECT', category=category)
        self.topic_a = Topic.objects.create(title='TEST_TOPIC_A', subject=self.subject)
        self.topic_b = Topic.objects.create(title='TEST_TOPIC_B', subject=self.subject)
        self.question_a = TrueFalseQuestion.objects\
            .create(question_text='TEST_QUESTION_A', answer=True, topic=self.topic_a)
        self.question_b = TextQuestion.objects\
            .create(question_text='TEST_QUESTION_B', answer='TEST_ANSWER', topic=self.topic_a)
        self.question_c = NumberQuestion.objects.create(question_text='TEST_QUESTION_C', answer=42, topic=self.topic_a)
        self.question_d = MultipleChoiceQuestion.objects.create(question_text='TEST_QUESTION_D', topic=self.topic_a)
        MultipleChoiceAnswer.objects.create(question=self.question_d, answer='TEST_ANSWER_A', correct=True)
        MultipleChoiceAnswer.objects.create(question=self.question_d, answer='TEST_ANSWER_B', correct=False)
        self.user = User.objects.create_user(username='TEST_USER', password='TEST_PASSWORD')
        self.player = Player.objects.create(user=self.user)
        PlayerTopic.objects.create(player=self.player, topic=self.topic_a)
        self.client.login(username='TEST_USER', password='TEST_PASSWORD')

    def test_post_truefalse_correct(self):
        post = {
            'question': self.question_a.id,
            'answer': 'True',
        }
        response = self.client.post('/quiz/', post)
        self.assertEquals(json.loads(response.content.decode()), self.question_a.answer_feedback_raw(post['answer']))

    def test_post_truefalse_question_not_int(self):
        response = self.client.post('/quiz/', {'question': 'NOT_INT'})
        self.assertEquals(json.loads(response.content.decode()), {})

    def test_post_truefalse_question_doesnt_exist(self):
        response = self.client.post('/quiz/', {'question': '1337'})
        self.assertEquals(json.loads(response.content.decode()), {})

    def test_select_topic_page(self):
        response = self.client.get('/quiz/select-topics/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context[0].dicts[3]['subject'], self.subject)
        self.assertEquals(response.context[0].dicts[3]['playerTopics'], [self.topic_a])

    def test_select_topic(self):
        response = self.client.post('/quiz/select-topics/', {
            'subject': 'TEST_SUBJECT',
            'topics': 'TEST_TOPIC_A',
        })
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, '/quiz')
        self.assertEquals(PlayerTopic.objects.all().count(), 1)
        self.assertEquals(PlayerTopic.objects.get().player, self.player)
        self.assertEquals(PlayerTopic.objects.get().topic, self.topic_a)

    def test_select_all_topics(self):
        response = self.client.post('/quiz/select-topics/', {
            'subject': 'TEST_SUBJECT',
            'topics': '',
        })
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, '/quiz')
        self.assertEquals(PlayerTopic.objects.all().count(), 2)

    def test_select_topics_no_data(self):
        response = self.client.post('/quiz/select-topics/', {})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, '/')

    def test_select_topics_no_subject(self):
        response = self.client.post('/quiz/select-topics/', {
            'subject': '',
            'topics': '',
        })
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, '/quiz/select-topics/')

    def test_select_topics_topic_doesnt_exist(self):
        response = self.client.post('/quiz/select-topics/', {
            'subject': 'TEST_SUBJECT',
            'topics': 'UNKNOWN_TOPIC',
        })
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, '/quiz')

    def test_select_topics_player_has_no_topics(self):
        PlayerTopic.objects.all().delete()
        response = self.client.get('/quiz/select-topics/')
        self.assertEquals(response.status_code, 200)

    def test_stats_default(self):
        response = self.client.get('/quiz/stats/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/quiz/stats/%r' % self.topic_a.id)

    def test_stats_default_with_nonexisting_topic(self):
        response = self.client.get('/quiz/stats/1337')
        self.assertEqual(response.status_code, 200)

    def test_stats_default_none_selected(self):
        PlayerTopic.objects.all().delete()
        response = self.client.get('/quiz/stats/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/quiz/stats/0')

    def test_question_page(self):
        response = self.client.get('/quiz/')
        self.assertEqual(response.status_code, 200)

    def test_question_page_without_topics(self):
        PlayerTopic.objects.all().delete()
        response = self.client.get('/quiz/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/quiz/select-topics')

    def test_question_page_answered_all(self):
        PlayerAnswer.objects.create(question=self.question_a, player=self.player, result=True)
        PlayerAnswer.objects.create(question=self.question_b, player=self.player, result=True)
        PlayerAnswer.objects.create(question=self.question_c, player=self.player, result=True)
        PlayerAnswer.objects.create(question=self.question_d, player=self.player, result=True)
        response = self.client.get('/quiz/')
        self.assertEqual(response.status_code, 200)

    def test_question_page_multiple_choice(self):
        self.question_a.delete()
        self.question_b.delete()
        self.question_c.delete()
        response = self.client.get('/quiz/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'quiz/multipleChoiceQuestion.html')

    def test_question_page_truefalse_question(self):
        self.question_b.delete()
        self.question_c.delete()
        self.question_d.delete()
        response = self.client.get('/quiz/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'quiz/trueFalseQuestion.html')

    def test_question_page_text_question(self):
        self.question_a.delete()
        self.question_c.delete()
        self.question_d.delete()
        response = self.client.get('/quiz/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'quiz/textQuestion.html')

    def test_question_page_number_question(self):
        self.question_a.delete()
        self.question_b.delete()
        self.question_d.delete()
        response = self.client.get('/quiz/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'quiz/numberQuestion.html')

    def test_stats_page(self):
        response = self.client.get('/quiz/stats/%r' % self.topic_a.id)
        self.assertEqual(response.status_code, 200)

    def test_report(self):
        response = self.client.post('/quiz/report/', {
            'question_id': self.question_a.id,
        })
        self.assertEqual(QuestionReport.objects.all().count(), 1)
        self.assertEqual(QuestionReport.objects.get().question.id, self.question_a.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/quiz')

    def test_report_delete_as_admin(self):
        self.user.is_superuser = True
        self.user.save()
        QuestionReport.objects.create(question=self.question_a, player=self.player)
        self.client.get('/quiz/viewreports/deletequestion/%r/' % self.question_a.id)
        # self.assertEqual(QuestionReport.objects.all().count(), 0)
        self.assertEqual(Question.objects.filter(pk=self.question_a.id).count(), 0)

    def test_report_delete_as_nonadmin(self):
        QuestionReport.objects.create(question=self.question_a, player=self.player)
        self.client.get('/quiz/viewreports/deletequestion/%r/' % self.question_a.id)
        self.assertEqual(Question.objects.filter(pk=self.question_a.id).count(), 1)

    def test_view_reports_as_admin(self):
        self.user.is_superuser = True
        self.user.save()
        response = self.client.get('/quiz/viewreports/')
        self.assertEqual(response.status_code, 200)

    def test_view_reports_as_nonadmin(self):
        response = self.client.get('/quiz/viewreports/')
        self.assertNotEqual(response.status_code, 200)

    def test_handle_reports_as_admin(self):
        QuestionReport.objects.create(question=self.question_a, player=self.player)
        self.user.is_superuser = True
        self.user.save()
        response = self.client.get('/quiz/viewreports/handlereport/%r/' % self.question_a.id)
        self.assertEqual(response.status_code, 200)

    def test_handle_reports_as_nonadmin(self):
        QuestionReport.objects.create(question=self.question_a, player=self.player)
        response = self.client.get('/quiz/viewreports/handlereport/%r/' % self.question_a.id)
        self.assertNotEqual(response.status_code, 200)
