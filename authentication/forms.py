from django import forms
from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError

class LoginForm(forms.Form):
    username = forms.CharField(max_length=15, label="username")
    password = forms.CharField(max_length=30, widget=forms.PasswordInput, label="password")

    def clean(self):
        form_data = self.cleaned_data

        try:
            user = authenticate(
                username = form_data['username'],
                password = form_data['password'],
            )
            if user is None:
                raise ValidationError({'password': 'Wrong username or password.'}, code='invalid')
        except KeyError:
            pass

        return form_data


class RegistrationForm(forms.Form):
    firstName = forms.CharField(max_length=15, label="firstName")
    lastName = forms.CharField(max_length=15, label="lastName")
    email = forms.EmailField(max_length=50, label="email")
    username= forms.CharField(max_length=15, label="username")
    password = forms.CharField(max_length=30, widget=forms.PasswordInput, label="password")
    passwordConfirm = forms.CharField(max_length=30, widget=forms.PasswordInput, label="passwordConfirm")