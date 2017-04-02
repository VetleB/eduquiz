from django import forms
from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

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

    def clean(self):
        form_data = self.cleaned_data
        try:
            try:
                User.objects.get(email=form_data["email"])
                raise forms.ValidationError({'email': 'E-mail already in use.'}, code='invalid')
            except User.DoesNotExist:
                pass

            try:
                User.objects.get(username=form_data["username"])
                raise forms.ValidationError({'username': 'Username taken. Please choose another one.'}, code='invalid')
            except User.DoesNotExist:
                pass

            if form_data["password"] != form_data["passwordConfirm"]:
                raise forms.ValidationError({'passwordConfirm': 'Passwords did not match. Try again.'}, code='invalid')



        except KeyError:
            pass

        return form_data


class ChangeUsernameForm(forms.Form):
    username = forms.CharField(max_length=15, label='username')

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangeUsernameForm, self).__init__(*args, **kwargs)

    def clean(self):
        form_data = self.cleaned_data
        try:
            User.objects.get(username=form_data['username'])
            raise forms.ValidationError({'username': 'Username taken. Please choose another one.'}, code='invalid')
        except User.DoesNotExist:
            pass
        except:
            pass

        return form_data

    def save(self):
        self.user.username = self.cleaned_data['username']
        self.user.save()
