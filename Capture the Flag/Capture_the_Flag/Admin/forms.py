from django import forms
from django.forms import ModelForm
from django import forms
from .models import *
from django.contrib.auth.models import User
from django.db.models import Q

#class QuestionForm(forms.Form):
#    title = models.CharField(max_length=255)
#    TYPE_CHOICES = [
#        ('T', 'Text'),
#        ('I', 'Image'),
#        ('M', 'Multiple Choice')
#    ]
#    REFEREE_RADIO = [
#        ('0', 'Nee'),
#        ('1', 'Ja')
#        ]
#    type = models.CharField(max_length=255, choices=TYPE_CHOICES)
#    omschrijving = models.CharField(max_length=255)
#    juist_antwoord = models.CharField(max_length=255)
#    downloadlink = models.CharField(max_length=255)
#    punten = models.IntegerField(default=0)
#    nakijken = models.IntegerField(choices=REFEREE_RADIO)

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

class ModifyQuestionForm(ModelForm):
    class Meta:
        model = Vraag
        fields = [
            'title', 
            'omschrijving',
            'juist_antwoord',
            'punten',
            'nakijken']
        widgets = {
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
    team_amount = forms.IntegerField(label='Aantal teams', min_value = 0)
    

class AssessForm(forms.Form):
    #points = forms.IntegerField(label='Score')
    correct = forms.BooleanField(label='Goedrekenen', required=False)

class LoginForm(ModelForm):
    class Meta:
        model = User
        fields = ['username',
            'password']

class RoundForm(ModelForm):
    class Meta:
        model = Ronde
        fields = ['duratie']
        #widgets = {
        #    'duratie' : form.IntegerField(attrs={'class': "duration-field"})}

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