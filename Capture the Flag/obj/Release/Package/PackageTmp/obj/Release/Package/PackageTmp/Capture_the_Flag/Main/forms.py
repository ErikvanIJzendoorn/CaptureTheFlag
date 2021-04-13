from django import forms 
from django.forms import ModelForm
from Capture_the_Flag.Admin.models import *

class TeamLoginForm(forms.Form):
    tournamentCode = forms.CharField(widget=forms.TextInput(attrs={
            'class' : 'form-control',
            'placeholder' : 'Toernooicode',
            'maxlength' : 24
            }))
    teamCode = forms.CharField(widget=forms.TextInput(attrs={
            'class' : 'form-control',
            'placeholder' : 'Teamcode',
            'maxlength' : 24
            }))

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
            'class' : 'form-control',
            'placeholder' : 'Gebruikersnaam',
            'maxlength' : 24
            }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
            'class' : 'form-control',
            'placeholder' : 'Wachtwoord',
            'maxlength' : 24
            }))