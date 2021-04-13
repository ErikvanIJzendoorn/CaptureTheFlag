from django import forms 
from django.forms import ModelForm
from Capture_the_Flag.Admin.models import *


class TeamLoginForm(forms.Form):
    tournamentCode = forms.CharField(label='Toernooicode', max_length=24)
    teamCode = forms.CharField(label='Team code', max_length=24)

class TeamMemberForm(ModelForm):
    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super(TeamMemberForm, self).__init__(*args, **kwargs)
        # there's a `fields` property now
        self.fields['studentnummer'].required = False
        self.fields['schermnaam'].required = False
    class Meta:
        model = Teamlid
        fields = [
            'studentnummer',
            'schermnaam'
        ]
        widgets = {
            'studentnummer' : forms.TextInput(attrs={'class' : 'form-control'}),
            'schermnaam' : forms.TextInput(attrs={'class' : 'form-control'})
            }
        

class SubmitAnswerForm(ModelForm):
    class Meta:
        model = Antwoord
        fields = [
            'antwoord'
        ]
        widgets = {
            'antwoord' : forms.Textarea(attrs={"rows":5, "cols":70})}

class SubmitImageAnswerForm(forms.Form):
    antwoord = forms.FileField()


class TeamNameForm(ModelForm):
    class Meta:
        model = Team
        fields = [
            'naam'
        ]
        widgets = {
            'naam': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teamnaam'})
        }

class TeamProfileForm(ModelForm):
    class Meta:
        model = Team
        fields = [
            'naam',
            'kleur'
            ]
        widgets = {
            'naam' : forms.TextInput(attrs={'class' : 'form-control'}),
            'kleur' : forms.TextInput(attrs={'class' : 'form-control'})
            }