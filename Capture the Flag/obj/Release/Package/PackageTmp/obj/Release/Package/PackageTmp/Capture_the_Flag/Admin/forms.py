from django import forms
from django.forms import ModelForm
from django import forms
from .models import *
from django.contrib.auth.models import User
from django.db.models import Q

class QuestionForm(ModelForm):
    class Meta:
        model = Vraag
        fields = ['type',
            'title', 
            'omschrijving',
            'juist_antwoord',
            'punten',
            'nakijken']
        widgets = {
            'type': forms.Select(attrs = {'onchange' : "changeType()", 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'omschrijving': forms.TextInput(attrs={'class': 'form-control'}),
            'juist_antwoord': forms.TextInput(attrs={'class': 'form-control'}),
            'punten': forms.NumberInput(attrs={'class': 'form-control'}),
            'nakijken': forms.NumberInput(attrs={'class': 'form-control'})
           }

class TournamentForm(ModelForm):
    class Meta:
        model = Toernooi
        fields = ['naam',
            'omschrijving',
            'type']
        widgets = {
            'type': forms.Select(attrs = {'onchange' : "changeType()", 'class': "form-control col-md-6"}),
            'naam': forms.TextInput(attrs={'class': "form-control col-md-6"}),
            'omschrijving': forms.TextInput(attrs={'class': "form-control col-md-6"}),
        }
            

class TeamForm(forms.Form):
    team_amount = forms.IntegerField(label='Aantal teams')

class AssessForm(forms.Form):
    #points = forms.IntegerField(label='Score')
    correct = forms.BooleanField(label='Goedrekenen', required=False)

class LoginForm(ModelForm):
    class Meta:
        model = User
        fields = ['username',
            'password']

class RondeForm(ModelForm):
    class Meta:
        model = Ronde
        fields = ['duratie']

class AssignScheidsrechterForm(forms.Form):
    gebruikers = forms.ModelChoiceField(queryset = User.objects.all())

    def __init__(self, *args, **kwargs):
        if 'mogelijkeScheidsrechters' in kwargs:
            self.mogelijkeScheidsrechters = kwargs.pop('mogelijkeScheidsrechters')
            super(AssignScheidsrechterForm, self).__init__(*args, **kwargs)
            self.fields['gebruikers'] = forms.ModelChoiceField(queryset = User.objects.exclude(~Q(username__in=self.mogelijkeScheidsrechters)))
        else:
            super(AssignScheidsrechterForm, self).__init__(*args, **kwargs)

class toernooibeheerderWijzigenForm(forms.Form):
    gebruikers = forms.ModelChoiceField(label='Nieuwe beheerder', queryset = User.objects.all())