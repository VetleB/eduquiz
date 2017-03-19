from django import forms
from django.core.exceptions import ValidationError

class MultipleChoiceQuestionForm(forms.Form):
    question = forms.CharField(max_length=100, label="Question")
    answer1 = forms.CharField(max_length=100, label="Alternative 1")
    correct1 = forms.BooleanField(label="Correct", required=False)
    answer2 = forms.CharField(max_length=100, label="Alternative 2")
    correct2 = forms.BooleanField(label="Correct", required=False)
    answer3 = forms.CharField(max_length=100, label="Alternative 3")
    correct3 = forms.BooleanField(label="Correct", required=False)
    answer4 = forms.CharField(max_length=100, label="Alternative 4")
    correct4 = forms.BooleanField(label="Correct", required=False)

    rating = forms.IntegerField(label="Rating")

    subject = forms.CharField(max_length=100, label="Subject")
    topics = forms.CharField(max_length=100, label="Topic")

    def clean(self):
        form_data = self.cleaned_data

        try:
            if not form_data['correct1'] and not form_data['correct2'] and not form_data['correct3'] and not form_data['correct4']:
                raise ValidationError({'correct4': 'One of the alteratives must be correct'}, code='invalid')
        except KeyError:
            pass

        return form_data

class TrueFalseQuestionForm(forms.Form):
    question = forms.CharField(max_length=100, label="Question")
    correct = forms.BooleanField(label="True", required=False)
    wrong = forms.BooleanField(label="False", required=False)

    rating = forms.IntegerField(label="Rating")

    subject = forms.CharField(max_length=100, label="Subject")
    topics = forms.CharField(max_length=100, label="Topic")

    def clean(self):
        form_data = self.cleaned_data

        try:
            if not form_data['correct'] and not form_data['wrong']:
                raise ValidationError({'correct': 'Is it true or false?'}, code='invalid')
        except KeyError:
            pass

        return form_data


class TextQuestionForm(forms.Form):
    question = forms.CharField(max_length=100, label="Question")
    answer = forms.CharField(max_length=100, label="Answer")

    rating = forms.IntegerField(label="Rating")

    text = forms.BooleanField(label="Text", required=False)
    number = forms.BooleanField(label="Number", required=False)

    subject = forms.CharField(max_length=100, label="Subject")
    topics = forms.CharField(max_length=100, label="Topic")

    def clean(self):
        form_data = self.cleaned_data

        try:
            if not form_data['text'] and not form_data['number']:
                raise ValidationError({'text': 'Is the answer text or a number?'}, code='invalid')
        except KeyError:
            pass

        return form_data


class ReportForm(forms.Form):
    # TODO: add all necessary fields
    question_text = forms.CharField(max_length=200)
    ambiguous = forms.BooleanField(label="Ambiguous", required=False)
    green_wrong = forms.BooleanField(label="Green_wrong", required=False)

    def clean(self):
        form_data = self.cleaned_data
        return form_data
