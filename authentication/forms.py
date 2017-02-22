from django import forms


class loginForm(forms.Form):
    username=forms.CharField(max_length=15, label="username")
    password=forms.CharField(widget=forms.PasswordInput)
