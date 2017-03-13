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
    correct = forms.BooleanField(label="Correct", required=False)

    rating = forms.IntegerField(label="Rating")

    subject = forms.CharField(max_length=100, label="Subject")
    topics = forms.CharField(max_length=100, label="Topic")

class TextQuestionForm(forms.Form):
    question = forms.CharField(max_length=100, label="Question")
    answer = forms.CharField(max_length=100, label="Answer")

    rating = forms.IntegerField(label="Rating")

    # True: text  False: number
    text = forms.BooleanField(label="Text", required=False)

    subject = forms.CharField(max_length=100, label="Subject")
    topics = forms.CharField(max_length=100, label="Topic")
