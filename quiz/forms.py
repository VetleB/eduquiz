from django import forms
from django.core.exceptions import ValidationError

class MultipleChoiceQuestionForm(forms.Form):
    question = forms.CharField(max_length=200, label="Question")

    answer1 = forms.CharField(max_length=100, label="Alternative 1")
    answer2 = forms.CharField(max_length=100, label="Alternative 2")
    answer3 = forms.CharField(max_length=100, label="Alternative 3")
    answer4 = forms.CharField(max_length=100, label="Alternative 4")

    correct = forms.CharField(label="Correct", required=False)

    rating = forms.IntegerField(label="Rating")

    subject = forms.CharField(max_length=100, label="Subject")
    topics = forms.CharField(max_length=100, label="Topic")

    def clean(self):
        form_data = self.cleaned_data

        try:
            if not form_data['correct']:
                raise ValidationError({'correct': 'One of the alteratives must be correct'}, code='invalid')
        except KeyError:
            pass

        return form_data

class TrueFalseQuestionForm(forms.Form):
    question = forms.CharField(max_length=200, label="Question")
    correct = forms.CharField(label="True", required=False)

    rating = forms.IntegerField(label="Rating")

    subject = forms.CharField(max_length=100, label="Subject")
    topics = forms.CharField(max_length=100, label="Topic")

    def clean(self):
        form_data = self.cleaned_data

        try:
            if not form_data['correct']:
                raise ValidationError({'correct': 'Is it true or false?'}, code='invalid')
        except KeyError:
            pass

        return form_data


class TextQuestionForm(forms.Form):
    question = forms.CharField(max_length=200, label="Question")
    answer = forms.CharField(max_length=100, label="Answer")

    rating = forms.IntegerField(label="Rating")

    text = forms.CharField(label="Text", required=False)

    subject = forms.CharField(max_length=100, label="Subject")
    topics = forms.CharField(max_length=100, label="Topic")

    def clean(self):
        form_data = self.cleaned_data

        try:
            if not form_data['text']:
                raise ValidationError({'text': 'Is the answer text or a number?'}, code='invalid')
        except KeyError:
            pass

        return form_data

class ReportForm(forms.Form):
    question_text = forms.CharField(max_length=200, label="Question text")
    red_right = forms.BooleanField(label="Red-right", required=False)
    green_wrong = forms.BooleanField(label="Green-wrong", required=False)
    unclear = forms.BooleanField(label="Unclear", required=False)
    off_topic = forms.BooleanField(label="Off-topic", required=False)
    inappropriate = forms.BooleanField(label="Inappropriate", required=False)
    other = forms.BooleanField(label="Other", required=False)
    comment = forms.CharField(label="Comment", required=False)

    def clean(self):
        form_data = self.cleaned_data
        return form_data
